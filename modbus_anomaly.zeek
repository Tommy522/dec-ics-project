@load base/protocols/modbus
@load base/frameworks/notice

module ModbusAnomaly;

export {
    redef enum Notice::Type += {
        ModbusAnomaly::UnauthorizedSetpointWrite,
        ModbusAnomaly::WriteFloodDetected
    };

    const baseline_value: count = 1500 &redef;
    const flood_threshold: count = 10 &redef;
    const flood_window: interval = 1sec &redef;
}

global write_counts: table[addr] of count &default=0 &create_expire=flood_window;

function check_flood(c: connection)
    {
    local src = c$id$orig_h;
    ++write_counts[src];

    if ( write_counts[src] > flood_threshold )
        {
        NOTICE([$note=ModbusAnomaly::WriteFloodDetected,
                $msg=fmt("Write flood: %s sent %d writes within %s",
                         src, write_counts[src], flood_window),
                $conn=c]);
        }
    }

event modbus_write_single_register_request(c: connection, headers: ModbusHeaders, address: count, value: count)
    {
    if ( address == 0 && value != baseline_value )
        {
        NOTICE([$note=ModbusAnomaly::UnauthorizedSetpointWrite,
                $msg=fmt("Unauthorized write to register %d: value=%d (expected baseline=%d)",
                         address, value, baseline_value),
                $conn=c]);
        }
    check_flood(c);
    }

event modbus_write_multiple_registers_request(c: connection, headers: ModbusHeaders, start_address: count, registers: ModbusRegisters)
    {
    if ( start_address == 0 && |registers| > 0 && registers[0] != baseline_value )
        {
        NOTICE([$note=ModbusAnomaly::UnauthorizedSetpointWrite,
                $msg=fmt("Unauthorized multi-register write starting at %d: register 0 value=%d (expected baseline=%d)",
                         start_address, registers[0], baseline_value),
                $conn=c]);
        }
    check_flood(c);
    }
