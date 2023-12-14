# Copyright lowRISC contributors.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

import sys

import chipwhisperer as cw
from fi_gear.utility import random_float_range

sys.path.append("../")
from util import check_version  # noqa: E402


class HuskyVCC:
    """ Initialize Husky for VCC glitching.

    Args:
        pll_frequency. The PLL frequency of the target.
        glitch_width_min: Lower bound for the glitch width.
        glitch_width_max: Upper bound for the glitch width.
        glitch_width_step: Step for the glitch width.
        trigger_delay_min: Lower bound for the trigger delay.
        trigger_delay_max: Upper bound for the trigger delay.
        trigger_step: Step for the trigger delay.
    """
    def __init__(self, pll_frequency: int, glitch_width_min: float,
                 glitch_width_max: float, glitch_width_step: float,
                 trigger_delay_min: int, trigger_delay_max: int, trigger_step: int):
        # Set Husky parameters.
        self.scope = None
        self.pll_frequency = pll_frequency

        # Set glitch parameter space.
        self.glitch_width_min = glitch_width_min
        self.glitch_width_max = glitch_width_max
        self.glitch_width_step = glitch_width_step
        self.trigger_delay_min = trigger_delay_min
        self.trigger_delay_max = trigger_delay_max
        self.trigger_step = trigger_step

        # Init husky.
        self.init_husky()

    def init_husky(self) -> None:
        """ Initialize husky.

        Configure Husky crowbar in such a way that the glitcher uses the HP
        MOSFET and a single glitch is clkgen_freq long.
        """
        check_version.check_husky("1.5.0")
        self.scope = cw.scope()

        if not self.scope._is_husky:
            raise RuntimeError("Only ChipWhisperer Husky is supported!")
        # Configure the clock.
        self.scope.clock.clkgen_freq = self.pll_frequency
        # Initialize the voltage glitching.
        self.scope.vglitch_setup('hp', default_setup=False)
        # Glitch output is high for glitch.repeat cycles. One cylce is
        # clkgen_freq.
        self.scope.glitch.output = "enable_only"

        # Configure trigger.
        self.scope.glitch.trigger_src = "ext_single"
        self.scope.trigger.triggers = "tio4"

    def arm_trigger(self, fault_parameters: dict) -> None:
        """ Arm the trigger.

        Configures the glitcher to inject a fault of width glitch.repeat cycles
        after the trigger delay.

        Args:
            A dict containing the FI parameters.
        """
        self.scope.glitch.repeat = fault_parameters['glitch_width']
        self.scope.glitch.ext_offset = fault_parameters['trigger_delay']
        self.scope.arm()

    def generate_fi_parameters(self) -> dict:
        """ Generate random voltage glitch parameters within the provided
            limits.

        Returns:
            A dict containing the FI parameters.
        """
        parameters = {}
        parameters["glitch_width"] = random_float_range(self.glitch_width_min,
                                                        self.glitch_width_max,
                                                        self.glitch_width_step)
        parameters["trigger_delay"] = random_float_range(self.trigger_delay_min,
                                                         self.trigger_delay_max,
                                                         self.trigger_step)
        return parameters

    def reset(self) -> None:
        """ Initialize husky.

        If the target crashes, Husky needs to be again initialized.
        """
        self.init_husky()