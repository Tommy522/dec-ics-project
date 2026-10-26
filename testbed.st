PROGRAM program0
  VAR
    baseline_speed AT %QW0 : INT;
    unprotected_value AT %QW1 : INT;
  END_VAR

  baseline_speed := 1500;

END_PROGRAM

CONFIGURATION Config0
  RESOURCE Res0 ON PLC
    TASK task0(INTERVAL := T#100ms, PRIORITY := 0);
    PROGRAM instance0 WITH task0 : program0;
  END_RESOURCE
END_CONFIGURATION
