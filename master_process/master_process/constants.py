class Constants(object):

    # Request Types
    GET = 'GET'
    POST = 'POST'

    # Redis Lap Keys
    LAP_COUNT = 'lap_count'
    LAP_SLOPE_1 = 'lap_m1'
    LAP_CONSTANT_1 = 'lap_c1'
    LAP_SLOPE_2 = 'lap_m2'
    LAP_CONSTANT_2 = 'lap_c2'
    LAP_START_TIME = 'lap_start_time'
    PROCESS_ID = 'process_id'

    # Lap Message Keys
    M1 = 'm1'
    C1 = 'c1'
    M2 = 'm2'
    C2 = 'c2'

    # Redis Key Suffix
    X_COORDINATE_SUFFIX = '-x'
    Y_COORDINATE_SUFFIX = '-y'
