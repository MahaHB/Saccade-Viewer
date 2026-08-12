import numpy as np
import time

class IPASTStats:



    sacc_marks={
        'unmarked': 1,#'not described below...'
           'noise': 2,# 'a spike in speed that resembles a microsacade but is most likely not a viable eye movement.'
           'micro': 3,#'just that; none of the below can be micro saccades.'
        'cor_pros': 4,#'a correct saccade during pro  trial; used to calculate SRT'
        'cor_anti': 5,#'a correct saccade during anti trial; used to calculate SRT'
        'dEr_pros': 6,#'a direction error during anti trial; used to calculate SRT'
        'dEr_anti': 7,#'a direction error during pro  trial; used to calculate SRT'
    'pre_cor_pros': 8,#'an anticipatory correct saccade during pro  trial; used to calculate SRT'
    'pre_cor_anti': 9,#'an anticipatory correct saccade during anti trial; used to calculate SRT'
    'pre_dEr_pros': 10,#'an anticipatory direction error during pro  trial; used to calculate SRT'
    'pre_dEr_anti': 11,#'an anticipatory direction error during anti trial; used to calculate SRT'
          'random': 12,#'a saccade in a non-stim & non-antistim direction once the stim has been displayed; used to calculate SRT'
         'REcover': 13,#'a saccade to the correct anti-direction soon after a dir_err saccade was made during an anti trial'
           'REset': 14,#'a saccade from stimulus back to fixation soon after a dir_err saccade was made during an anti trial'
         'REbound': 15,#'a saccade somewhere other than stim or anti-stim soon after a dir_err saccade was made during an anti trial'
         'RElapse': 16,#'a saccade to the anti direction soon after a correct saccade was made to the stim during a pro  trial'
     'to_fixation': 17,#'a saccade toward fixation'
       'fix_break': 18,#'a saccade away from fixation once fixation has been made prior to stim onset'
         'go_back': 19,#'a saccade back to fixation after fixation has been made & broke; indicating a false-start type event.'
            'step': 20#'undefinable'

    }


    def __init__(self):

        pass



