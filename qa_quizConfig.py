import json

"""
All config marked as "Alt" is alterable by the user
"""

keys_title = 'ttl' # ttl = title
keys_quizTaker_customConfig = 'acqc' # acqc = Allow Custom Quiz Configuration
keys_questions_partOrAll = 'qpoa' # qpoa = Questions Part Or All
keys_questions_divistionFactor = "qsdf" # qsdf = Questions Sampling Div Factor
keys_deductions_mode = "dma" # dma = Deductions Mode Allow
keys_deduction_perPoint = 'pdpir' # pdpir = Point Deductions Per Incorrect Response
keys_inDist = 'dist' # dist = Distribution

values_qspa_part = 'part'
values_qspa_all = 'all'

default_configuration = {
    keys_title: 'Quizzing Application v2.x',
    keys_quizTaker_customConfig: False, # Alt
    keys_questions_partOrAll: values_qspa_part, # Alt
    keys_questions_divistionFactor: 2, # Alt
    keys_deductions_mode: False, # Alt
    keys_deduction_perPoint: 1, # Alt
    keys_inDist: True
}

default_configuration_str = json.dumps(default_configuration, indent=4)
