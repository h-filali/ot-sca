# Copyright lowRISC contributors.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0
"""Communication interface for the ML-DSA SCA application on OpenTitan.

Communication with OpenTitan happens over the uJson command interface.
"""
import json
import time
from typing import Optional

class OTMLDSA:
    def __init__(self, target, protocol: str) -> None:
        self.target = target
        self.simple_serial = True
        if protocol == "ujson":
            self.simple_serial = False

    def _ujson_ml_dsa_sca_cmd(self):
        # TODO: without the delay, the device uJSON command handler program
        # does not recognize the commands. Tracked in issue #256.
        time.sleep(0.01)
        self.target.write(json.dumps("MlDsaSca").encode("ascii"))

    def ml_dsa_sca_read_response(self, num_attempts: Optional[int] = 100):
        """ Reads back the "result" response from the device.
        """
        read_counter = 0
        while read_counter < num_attempts:
            read_line = str(self.target.readline())
            if "RESP_OK" in read_line:
                json_string = read_line.split("RESP_OK:")[1].split(" CRC:")[0]
                try:
                    if "result" in json_string:
                        return json.loads(json_string)["result"]
                except Exception:
                    raise Exception("Acknowledge error: Device and host not in sync")
            else:
                read_counter += 1
        raise Exception("Acknowledge error: Device and host not in sync")

    def init(self):
        """ Initializes ML-DSA on the target.
        Args:
            -
        Returns:
            The device ID of the device.
        """
        if not self.simple_serial:
            # MlDsaSca command.
            self._ujson_ml_dsa_sca_cmd()
            # Init the ML-DSA application.
            self.target.write(json.dumps("Init").encode("ascii"))
            # Read back device ID from device.
            return self.read_response(max_tries=30)

    def ml_dsa_vec_reject_batch_fvsr(self, data: int, num_segments: list[int]):
        """ Start FVSR execution for rejection sampling in ML-DSA.
        Args:
            num_segments: The number of times the app should be executed.
            data: The fixed vector used for FVSR execution.
        """
        # MlDsaSca command.
        self._ujson_ml_dsa_sca_cmd()
        # NttFvsr command.
        self.target.write(json.dumps("RejectFvsr").encode("ascii"))
        # Send the number of iterations and the fixed vector.
        time.sleep(0.01)
        data = {"data": [x for x in data],
                "data_length": 4*len(data),
                "iterations": num_segments}
        self.target.write(json.dumps(data).encode("ascii"))

    def ml_dsa_decompose_batch_fvsr(self, data: int, num_segments: list[int]):
        """ Start FVSR execution for decompose in ML-DSA.
        Args:
            num_segments: The number of times the app should be executed.
            data: The fixed vector used for FVSR execution.
        """
        # MlDsaSca command.
        self._ujson_ml_dsa_sca_cmd()
        # NttFvsr command.
        self.target.write(json.dumps("DecomposeFvsr").encode("ascii"))
        # Send the number of iterations and the fixed vector.
        time.sleep(0.01)
        data = {"data": data,
                "data_length": 4,
                "iterations": num_segments}
        self.target.write(json.dumps(data).encode("ascii"))

    def ml_dsa_vec_add_batch_fvsr(self, data: int, num_segments: list[int]):
        """ Start FVSR execution for vector addition in ML-DSA.
        Args:
            num_segments: The number of times the app should be executed.
            data: The fixed vector used for FVSR execution.
        """
        # MlDsaSca command.
        self._ujson_ml_dsa_sca_cmd()
        # NttFvsr command.
        self.target.write(json.dumps("VecAddFvsr").encode("ascii"))
        # Send the number of iterations and the fixed vector.
        time.sleep(0.01)
        data = {"data": [x for x in data],
                "data_length": 4*len(data),
                "iterations": num_segments}
        self.target.write(json.dumps(data).encode("ascii"))

    def ml_dsa_vec_sub_batch_fvsr(self, data: int, num_segments: list[int]):
        """ Start FVSR execution for vector subtraction in ML-DSA.
        Args:
            num_segments: The number of times the app should be executed.
            data: The fixed vector used for FVSR execution.
        """
        # MlDsaSca command.
        self._ujson_ml_dsa_sca_cmd()
        # NttFvsr command.
        self.target.write(json.dumps("VecSubFvsr").encode("ascii"))
        # Send the number of iterations and the fixed vector.
        time.sleep(0.01)
        data = {"data": [x for x in data],
                "data_length": 4*len(data),
                "iterations": num_segments}
        self.target.write(json.dumps(data).encode("ascii"))

    def ml_dsa_vec_mul_batch_fvsr(self, data: int, num_segments: list[int]):
        """ Start FVSR execution for vector multiplication in ML-DSA.
        Args:
            num_segments: The number of times the app should be executed.
            data: The fixed vector used for FVSR execution.
        """
        # MlDsaSca command.
        self._ujson_ml_dsa_sca_cmd()
        # NttFvsr command.
        self.target.write(json.dumps("VecMulFvsr").encode("ascii"))
        # Send the number of iterations and the fixed vector.
        time.sleep(0.01)
        data = {"data": [x for x in data],
                "data_length": 4*len(data),
                "iterations": num_segments}
        self.target.write(json.dumps(data).encode("ascii"))

    def ml_dsa_vec_mac_batch_fvsr(self, data: int, num_segments: list[int]):
        """ Start FVSR execution for vector MAC in ML-DSA.
        Args:
            num_segments: The number of times the app should be executed.
            data: The fixed vector used for FVSR execution.
        """
        # MlDsaSca command.
        self._ujson_ml_dsa_sca_cmd()
        # NttFvsr command.
        self.target.write(json.dumps("VecMacFvsr").encode("ascii"))
        # Send the number of iterations and the fixed vector.
        time.sleep(0.01)
        data = {"data": [x for x in data],
                "data_length": 4*len(data),
                "iterations": num_segments}
        self.target.write(json.dumps(data).encode("ascii"))

    def ml_dsa_vec_ntt_batch_fvsr(self, data: int, num_segments: list[int]):
        """ Start FVSR execution for NTT in ML-DSA.
        Args:
            num_segments: The number of times the app should be executed.
            data: The fixed vector used for FVSR execution.
        """
        # MlDsaSca command.
        self._ujson_ml_dsa_sca_cmd()
        # NttFvsr command.
        self.target.write(json.dumps("NttFvsr").encode("ascii"))
        # Send the number of iterations and the fixed vector.
        time.sleep(0.01)
        data = {"data": [x for x in data],
                "data_length": 4*len(data),
                "iterations": num_segments}
        self.target.write(json.dumps(data).encode("ascii"))

    def ml_dsa_vec_intt_batch_fvsr(self, data: int, num_segments: list[int]):
        """ Start FVSR execution for INTT in ML-DSA.
        Args:
            num_segments: The number of times the app should be executed.
            data: The fixed vector used for FVSR execution.
        """
        # MlDsaSca command.
        self._ujson_ml_dsa_sca_cmd()
        # NttFvsr command.
        self.target.write(json.dumps("InttFvsr").encode("ascii"))
        # Send the number of iterations and the fixed vector.
        time.sleep(0.01)
        data = {"data": [x for x in data],
                "data_length": 4*len(data),
                "iterations": num_segments}
        self.target.write(json.dumps(data).encode("ascii"))

    def start_test(self, testname: str, arg1 = None, arg2 = None) -> None:
        """ Start the selected test.

        Call the function selected in the config file. Uses the getattr()
        construct to call the function.

        Args:
            testname: The test to start
            arg1: The first argument passed to the test.
            arg2: The second argument passed to the test.
        """
        test_function = getattr(self, testname)
        if arg1 is not None and arg2 is None:
            test_function(arg1)
        elif arg2 is not None:
            test_function(arg1, arg2)
        else:
            test_function()

    def read_response(self, max_tries: Optional[int] = 1) -> str:
        """ Read response from ML-DSA SCA framework.
        Args:
            max_tries: Maximum number of attempts to read from UART.

        Returns:
            The JSON response of OpenTitan.
        """
        it = 0
        while it != max_tries:
            read_line = str(self.target.readline())
            if "RESP_OK" in read_line:
                return read_line.split("RESP_OK:")[1].split(" CRC:")[0]
            it += 1
        return ""
