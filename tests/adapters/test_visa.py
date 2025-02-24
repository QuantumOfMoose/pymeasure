#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
import importlib.util

import pytest
from pytest import approx

from pymeasure.adapters import VISAAdapter
from pymeasure.instruments import Instrument

# This uses a pyvisa-sim default instrument, we could also define our own.
SIM_RESOURCE = 'ASRL2::INSTR'

is_pyvisa_sim_installed = bool(importlib.util.find_spec('pyvisa_sim'))
if not is_pyvisa_sim_installed:
    pytest.skip('PyVISA tests require the pyvisa-sim library', allow_module_level=True)


@pytest.fixture
def adapter():
    return VISAAdapter(SIM_RESOURCE, visa_library='@sim',
                       read_termination="\n")


def test_visa_version():
    assert VISAAdapter.has_supported_version()


def test_correct_visa_kwarg():
    """Confirm that the query_delay kwargs gets passed through to the VISA connection."""
    instr = Instrument(adapter=SIM_RESOURCE, name='delayed', query_delay=0.5, visa_library='@sim')
    assert instr.adapter.connection.query_delay == approx(0.5)


def test_correct_visa_asrl_kwarg():
    """Confirm that the asrl kwargs gets passed through to the VISA connection."""
    a = VISAAdapter(SIM_RESOURCE, visa_library='@sim',
                    asrl={'read_termination': "\rx\n"})
    assert a.connection.read_termination == "\rx\n"


def test_open_gpib():
    a = VISAAdapter(5, visa_library='@sim')
    assert a.resource_name == "GPIB0::5::INSTR"


def test_write_read(adapter):
    adapter.write(":VOLT:IMM:AMPL?")
    assert float(adapter.read()) == 1


def test_write_bytes_read_bytes(adapter):
    adapter.write_bytes(b"*IDN?\r\n")
    assert adapter.read_bytes(22) == b"SCPI,MOCK,VERSION_1.0\n"


def test_write_bytes_read(adapter):
    adapter.write_bytes(b"*IDN?\r\n")
    assert adapter.read() == "SCPI,MOCK,VERSION_1.0"


def test_write_read_bytes(adapter):
    adapter.write("*IDN?")
    assert adapter.read_bytes(22) == b"SCPI,MOCK,VERSION_1.0\n"


def test_visa_adapter(adapter):
    assert repr(adapter) == f"<VISAAdapter(resource='{SIM_RESOURCE}')>"

    assert adapter.ask("*IDN?") == "SCPI,MOCK,VERSION_1.0"

    adapter.write("*IDN?")
    assert adapter.read() == "SCPI,MOCK,VERSION_1.0"


def test_visa_adapter_ask_values(adapter):
    assert adapter.ask_values(":VOLT:IMM:AMPL?", separator=",") == [1.0]


def test_visa_adapter_write_binary_values(adapter):
    adapter.write_binary_values("OUTP", [1], datatype='B')
