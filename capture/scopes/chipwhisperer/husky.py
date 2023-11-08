# Copyright lowRISC contributors.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

import time

import chipwhisperer as cw
import numpy as np
from scopes.chipwhisperer.cw_segmented import CwSegmented

SAMPLING_RATE_MAX = 200e6


class Husky:
    def __init__(self, scope_gain, num_cycles, num_segments, offset_cycles,
                 pll_frequency, target_clk_mult):
        self.scope = None
        self.scope_gain = scope_gain
        # In our setup, Husky operates on the PLL frequency of the target and
        # multiplies that by an integer number to obtain the sampling rate.
        # Note that the sampling rate must be at most 200 MHz.
        self.clkgen_freq = pll_frequency
        self.adc_mul = int(SAMPLING_RATE_MAX // pll_frequency)
        self.sampling_rate = self.clkgen_freq * self.adc_mul

        # The target runs on the PLL clock but uses internal clock dividers and
        # multiplier to produce the clock of the target block.
        self.target_freq = pll_frequency * target_clk_mult

        # The scope is configured in terms of samples. For Husky, the number of
        # samples must be divisble by 3 for batch captures.
        sampling_target_ratio = self.sampling_rate / self.target_freq
        self.offset_samples = int(offset_cycles * sampling_target_ratio)
        self.num_samples = int(num_cycles * sampling_target_ratio)
        if self.num_samples % 3:
            self.num_samples = self.num_samples + 3 - (self.num_samples % 3)

        self.num_segments = num_segments
        self.scope = None

    def initialize_scope(self):
        """Initializes chipwhisperer scope."""
        scope = cw.scope()
        scope.gain.db = self.scope_gain
        scope.adc.basic_mode = "rising_edge"
        if not scope._is_husky:
            raise RuntimeError("Only ChipWhisperer Husky is supported!")

        scope.clock.clkgen_src = 'extclk'
        scope.clock.clkgen_freq = self.clkgen_freq
        scope.clock.adc_mul = self.adc_mul
        scope.clock.extclk_monitor_enabled = False
        scope.adc.samples = self.num_samples
        if self.offset_samples >= 0:
            scope.adc.offset = self.offset_samples
        else:
            scope.adc.offset = 0
            scope.adc.presamples = -self.offset_samples
        scope.trigger.triggers = "tio4"
        scope.io.tio1 = "serial_tx"
        scope.io.tio2 = "serial_rx"
        scope.io.hs2 = "disabled"

        # Make sure that clkgen_locked is true.
        scope.clock.clkgen_src = 'extclk'

        # Wait for ADC to lock.
        ping_cnt = 0
        while not scope.clock.adc_locked:
            if ping_cnt == 3:
                raise RuntimeError(
                    f'ADC failed to lock (attempts: {ping_cnt}).')
            ping_cnt += 1
            time.sleep(0.5)
        self.scope = scope

    def configure_batch_mode(self):
        if self.num_segments != 1:
            self.scope = CwSegmented(num_samples=self.num_samples,
                                     offset_samples=self.offset_samples,
                                     scope_gain=self.scope.gain.db,
                                     scope=self.scope,
                                     clkgen_freq=self.scope.clock.clkgen_freq,
                                     adc_mul=self.adc_mul)
            self.scope.num_segments = self.num_segments

    def arm(self):
        self.scope.arm()

    def capture_and_transfer_waves(self, target=None):
        if self.num_segments == 1:
            ret = self.scope.capture(poll_done=False)
            i = 0
            while not target.is_done():
                i += 1
                time.sleep(0.05)
                if i > 100:
                    print("Warning: Target did not finish operation")
            if ret:
                print("Warning: Timeout happened during capture")

            # Get Husky trace (single mode only) and return as array with one item
            return np.array([self.scope.get_last_trace(as_int=True)])

        # Batch mode
        return self.scope.capture_and_transfer_waves()
