#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2018 <+YOU OR YOUR COMPANY+>.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

import numpy as np
from gnuradio import gr, gr_unittest
from gnuradio import blocks
from equisat_4fsk_block_decode import equisat_4fsk_block_decode
from equisat_4fsk_preamble_detect import equisat_4fsk_preamble_detect
from scipy.io import wavfile
import pmt
import time
import binascii

# sample packet (EQUiSat string repeated 50 times)
packet_raw_EQUiSatx50 = [8027, -175, -305, -256, -260, -396, -104, -266, -649, -9598, -10467, 8514, 9704, -8817, -10206, 8927, 9356, -9143, -9955, 9247, 9035, -9405, -9700, 9572, 8762, -9689, -9376, 9776, 8510, -9844, -9227, 9982, 8398, -10080, -9078, 10137, 8240, -10214, -8883, 10240, 8049, -10170, -8790, 10274, 8006, -10342, -8654, 10338, 7974, -10280, -8693, 10434, 7946, -10418, -8710, 10328, 7971, -10313, -8711, 10373, 7954, -10233, -8804, 10302, 8109, -10312, -8805, 10245, 8129, -10191, -8891, 10210, 8185, -10101, -9030, 10095, 8230, -10101, -9063, 10024, 8405, -9988, -9180, 9941, 8470, -9824, -9274, 9854, 8541, -9832, -9355, 9841, 8687, -9631, -9567, 9699, 8785, -9666, -9475, 9572, 8864, -9549, -9591, 9541, 8967, -9456, -9729, 9449, 8967, -9469, -9635, 9364, 9053, -9289, -9876, 9353, 9085, -9321, -9873, 9237, 9109, -9264, -9851, 9174, 9247, -9215, -9989, 9223, 9179, -9300, -9932, 9315, 9199, -9174, -9985, 9181, 9285, -9161, -10021, 9146, 9264, -9238, -9921, 9124, 9263, -9165, -9973, 9201, 9270, -9083, -9988, 9136, 9212, -9205, -9968, 9223, 9193, -9220, -9887, 9175, 9154, -9227, -9997, 9220, 9159, -9277, -9966, 9237, 9157, -9303, -9862, 9238, 9181, -9234, -9960, 9301, 9089, -9266, -9794, 9265, 9138, -9368, -9760, 9349, 9063, -9288, -9840, 9397, 9127, -9241, -10031, 9348, 9909, 3614, -3243, 2835, -3471, 2796, -9465, 8626, -8640, 8968, 3427, -2616, 8503, -8762, -10702, 1889, -2618, 9873, 9746, -2779, -9738, 2674, 9219, -3223, -9973, -3755, 2925, 3430, 3386, 3258, 3297, 3303, 3354, 3141, 2966, -3068, 2224, -10261, -10661, -10852, -10656, -10851, -10583, -10230, 2331, -3194, 3348, 3319, 2918, -4020, -9690, 3500, 10171, 9841, 2872, -2784, 2532, -4391, -8913, 10325, 10170, 9283, -3609, -3597, -3860, -3780, -3717, -2993, 2566, -3183, 3435, 3832, 9695, 4118, 9137, -4015, -4406, -8599, 9819, 3929, 9030, -4199, -2190, 1185, -10055, -3265, -4196, -2809, 4534, 9319, 3069, 3712, 2247, -4774, -9924, -4854, -7950, 7915, -11594, -8904, -4877, -10887, -10707, -8951, 3659, 3097, 3467, 3274, 3265, 3284, 3217, 3308, 3602, 1003, -11097, -10570, -11021, -10773, -10723, -10682, -10591, -10813, -11118, -7432, 8587, -3197, 3171, -5650, -8756, 4974, 10621, 7686, -2903, 4153, 1925, -5633, -7374, 11252, 10269, 8225, -4104, -3227, -5639, -7163, 10142, 2679, 2417, -2901, 3520, 4496, 9561, 2826, 3467, 5087, 6125, -7877, 10243, 3967, 8574, -4570, -1701, 298, -7333, 8912, -3691, 4008, 4417, 9370, 2860, 3842, 1555, -2736, 4136, -110, -6970, 7450, -12332, -8646, -4907, -11092, -10916, -6535, 6899, -9459, 4613, 2687, 3506, 3357, 3377, 3308, 3296, 3203, 3005, 5251, 6588, -11655, -10223, -11096, -10737, -10743, -10733, -10711, -10954, -9339, -3252, -5376, -8773, 5326, 10671, 7479, -2671, 2807, -5715, -11270, -6807, 11218, 10430, 7920, -4225, -3121, -5854, -7164, 12060, 7054, -4110, -2109, 3135, 4722, 9357, 2914, 3782, 1665, -2291, 714, -9287, 5941, 7497, -4235, -1666, 291, -7578, 10208, 3734, 9761, 4173, 9646, 2877, 3787, 1980, -2886, 3391, 4286, 9767, 1888, -4756, -9770, -4528, -11171, -10841, -7504, 7814, -11432, -9158, -4116, -2921, 3486, 3218, 3384, 3362, 3256, 3278, 3223, 3276, 3439, 1672, -10641, -10678, -10949, -10698, -10703, -10523, -10896, -10752, -9164, 9431, 3875, 10621, 8999, -2590, 2696, -4430, -9431, 3379, 9500, 4248, 9217, -3426, -3621, -4635, -9041, 10393, 10143, 9360, -3027, 3426, 3725, 9769, 3307, 3495, 2515, -3223, 3361, 3841, 8480, -9827, -3436, -3610, 2165, -9043, 9650, 3688, 9656, -3609, -4028, -9651, 3095, 2479, -2922, 3268, 3743, 9706, 3291, 3568, 2674, -3995, -10782, -10714, -9186, 8131, -10287, -9813, -4654, -10588, -10667, -9898, 3040, 3196, 3491, 3265, 3332, 3245, 3259, 3341, 2692, -4220, -10571, -10801, -10855, -10770, -10726, -10585, -10862, -10933, -8981, 10266, 8808, -2443, 2735, -4606, -9370, 4006, 10095, 8809, -2064, 9213, -4053, -4365, -8780, 10817, 10196, 8920, -3717, -3492, -4978, -9110, 3690, 3124, 2455, -2956, 3416, 4236, 9599, 2885, 3686, 3490, 778, -8024, 9987, 3865, 8836, -4297, -2126, 856, -8989, 2813, -3374, 3713, 4306, 9587, 2980, 3791, 1791, -2887, 5180, 6351, -7657, 8017, -11988, -8847, -4802, -11012, -10895, -7603, 9909, 2733, 3780, 3190, 3311, 3288, 3265, 3254, 3224, 3432, 2385, -4917, -10735, -10810, -10895, -10736, -10702, -10687, -10790, -11085, -8789, 3916, 2069, -5061, -9059, 4910, 10555, 7863, -2794, 2550, -2803, 903, -7996, 11558, 10101, 8323, -4000, -3305, -5562, -7434, 10113, 2703, 2549, -2944, 3516, 4454, 9543, 2989, 3759, 1671, -1652, 11166, 8645, 4847, 8477, -4293, -2024, 750, -8016, 10163, 3686, 9924, 3989, 9770, 2982, 3595, 2161, -3025, 3337, 4116, 9916, 1051, -10597, -9859, -4603, -10973, -10609, -8613, 8235, -10811, -10328, -9846, 3261, 3093, 3512, 3319, 3286, 3259, 3165, 3359, 3391, 1907, -10467, -10681, -10943, -10728, -10720, -10640, -10988, -10491, -9514, 8192, -9283, 3800, 9729, 9462, -2694, 2647, -4194, -9637, 2217, -2616, 10539, 9006, -2944, -3789, -4405, -9171, 10219, 10151, 9543, -3016, 3378, 3637, 9771, 3409, 3514, 2630, -2932, 3050, 2606, -2441, 8980, -3184, -3096, 1896, -8969, 9679, 3557, 9580, -2535, 9729, 3351, 3552, 2823, -3095, 3059, 3580, 9713, 3510, 3398, 2900, -3660, -10695, -10552, -9921, 8383, -9532, -10289, -4658, -9656, 2711, 3199, 3509, 3275, 3316, 3307, 3232, 3273, 3314, 2883, -3813, -10437, -10892, -11047, -10783, -10762, -10647, -10716, -10858, -10427, -3283, 9602, 9852, -2404, 2545, -3732, -9827, 2892, 10055, 10045, 3179, -3192, -3973, -4116, -9524, 9892, 10168, 9920, -3461, -4026, -9452, 9449, 3323, 3599, 2758, -3171, 3084, 3790, 9806, 2218, -9335, -3850, 2081, -9075, 9475, 3741, 9567, -3137, -3300, 2584, -3103, 2778, -3276, 3265, 3533, 9760, 3414, 3424, 2865, -3339, -4391, -10298, -9670, 8151, -9915, -9989, -4692, -10313, -10723, -10426, -3539, 3002, 3374, 3330, 3289, 3270, 3170, 3416, 3268, 2405, -10087, -10823, -10882, -10761, -10813, -10694, -10676, -11017, -10525, -10089, 8804, -2651, 2835, -4071, -9626, 3230, 10010, 9398, -2764, 3482, 2515, -3990, -9329, 10038, 10197, 9540, -3250, -3739, -4556, -8882, 9709, 3051, 3041, -3203, 3400, 3817, 9820, 3118, 3659, 3963, 8103, -8700, 9990, 3644, 9201, -3796, -2741, 1449, -8521, 9115, -3515, 3776, 3876, 9642, 3137, 3589, 2145, -2849, 3456, 1179, -8100, 8140, -11062, -9377, -4721, -10805, -10566, -8536, 7941, -9510, 3889, 2761, 3588, 3315, 3297, 3318, 3301, 3142, 3240, 4426, 7753, -10980, -10427, -11079, -10727, -10751, -10727, -10760, -10882, -9786, -3594, -4910, -9202, 4604, 10367, 8210, -2763, 2929, -5216, -10975, -7828, 10884, 10327, 8455, -3926, -3339, -5521, -7729, 11758, 7454, -3888, -2372, 3108, 4506, 9487, 2909, 3744, 1864, -2439, 921, -9287, 5743, 7625, -4169, -1760, 379, -7660, 10221, 3751, 9741, 4145, 9685, 2886, 3731, 1884, -2853, 3393, 4309, 9760, 1832, -4880, -9670, -4545, -11225, -10919, -7073, 7583, -11695, -9000, -4046, -2830, 3566, 3178, 3441, 3315, 3300, 3262, 3219, 3270, 3475, 1265, -10894, -10572, -10933, -10733, -10707, -10567, -10804, -10933, -8209, 9589, 3831, 11029, 8312, -2704, 2838, -5048, -9000, 4259, 9134, 4422, 8861, -3964, -3352, -5117, -8332, 11026, 10169, 8692, -3015, 3497, 4077, 9665, 3062, 3601, 2139, -3070, 3518, 4265, 7688, -10096, -3179, -3248, 1512, -8537, 10051, 3726, 9328, -4011, -4408, -9306, 3622, 2030, -2777, 3380, 4091, 9591, 3018, 3693, 2346, -4516, -10844, -10917, -8159, 7925, -11107, -9257, -4794, -10744, -10721, -9394, 3449, 3092, 3526, 3275, 3214, 3235, 3241, 3420, 2512, -4610, -10642, -10763, -10868, -10738, -10681, -10634, -10803, -11045, -8333, 10898, 8124, -2514, 2790, -5035, -9171, 4438, 10317, 8293, -1835, 9036, -4240, -4559, -8463, 10979, 10217, 8628, -3881, -3439, -5163, -8997, 3856, 3102, 2304, -2889, 3466, 4286, 9532, 2844, 3693, 3501, 585, -7892, 10009, 3902, 8781, -4358, -2017, 817, -8948, 2844, -3346, 3783, 4341, 9529, 2981, 3788, 1806, -2898, 5179, 6417, -7679, 8075, -11931, -8928, -4771, -10981, -10839, -7783, 9899, 2743, 3754, 3173, 3301, 3312, 3257, 3218, 3255, 3356, 2438, -4785, -10694, -10758, -10891, -10756, -10699, -10673, -10780, -10963, -9017, 3736, 2194, -4740, -9176, 4650, 10418, 8221, -2873, 2644, -2917, 1124, -8309, 11315, 10040, 8595, -3886, -3384, -5335, -7842, 10036, 2804, 2656, -3064, 3485, 4274, 9593, 3121, 3652, 1970, -1970, 10968, 8984, 4590, 8731, -3955, -2415, 1140, -8353, 10040, 3552, 9954, 3906, 9840, 3143, 3537, 2383, -3116, 3193, 3951, 9854, 1575, -10341, -10077, -4544, -10923, -10519, -9209, 8369, -10324, -10344, -10147, 3033, 3133, 3544, 3279, 3335, 3283, 3167, 3385, 3246, 2294, -10164, -10748, -10906, -10753, -10728, -10659, -11051, -10426, -10049, 8290, -9091, 3367, 9667, 9750, -2647, 2597, -3809, -9757, 2181, -2721, 10246, 9341, -2743, -3885, -4212, -9436, 9973, 10193, 9690, -2906, 3265, 3557, 9782, 3471, 3430, 2712, -2930, 2938, 2810, -2500, 8932, -3099, -3249, 1997, -9066, 9654, 3575, 9639, -2564, 9708, 3382, 3496, 2826, -3102, 3057, 3552, 9688, 3507, 3466, 2880, -3623, -10693, -10521, -10012, 8286, -9516, -10356, -4646, -9682, 2694, 3156, 3497, 3272, 3294, 3285, 3193, 3251, 3364, 2829, -3860, -10386, -10858, -10836, -10849, -10748, -10650, -10673, -10816, -10394, -3158, 9731, 9690, -2441, 2566, -3911, -9716, 3132, 10108, 10019, 3064, -3272, -3946, -4279, -9410, 10011, 10161, 9799, -3497, -4110, -9312, 9558, 3221, 3625, 2634, -3145, 3181, 3849, 9863, 1927, -9384, -3645, 1909, -9044, 9592, 3737, 9480, -3290, -3179, 2536, -3109, 2800, -3318, 3249, 3673, 9729, 3409, 3417, 2794, -3343, -4512, -10373, -9346, 8086, -10224, -9877, -4686, -10408, -10775, -10394, -3454, 3047, 3331, 3376, 3266, 3243, 3206, 3363, 3305, 2240, -10296, -10722, -10988, -10740, -10796, -10694, -10662, -10971, -10527, -9952, 8797, -2726, 2871, -4191, -9481, 3498, 10069, 9262, -2777, 3599, 2449, -4154, -9112, 10228, 10170, 9407, -3406, -3689, -4625, -8764, 9851, 3003, 2946, -3195, 3302, 3892, 9804, 3079, 3613, 4049, 7881, -8742, 10036, 3663, 9228, -3864, -2655, 1335, -8415, 9161, -3570, 3777, 3868, 9655, 3063, 3617, 2181, -2785, 3497, 1106, -8076, 8135, -11251, -9468, -4695, -10912, -10616, -8558, 7872, -9445, 3989, 2782, 3584, 3332, 3294, 3295, 3250, 3124, 3239, 4474, 7748, -10944, -10405, -11098, -10721, -10753, -10776, -10795, -10876, -9747, -3609, -4877, -9307, 4536, 10377, 8263, -2784, 3013, -5193, -10951, -7875, 10850, 10298, 8536, -3944, -3348, -5406, -7776, 11672, 7585, -3835, -2406, 3155, 4491, 9501, 2977, 3657, 1960, -2482, 1025, -9370, 5657, 7684, -4097, -1898, 501, -7771, 10164, 3703, 9797, 4179, 9658, 2885, 3706, 1914, -2906, 3446, 4238, 9692, 1871, -4871, -9854, -4483, -11255, -10879, -7244, 7640, -11532, -9118, -4087, -2884, 3551, 3184, 3339, 3352, 3294, 3241, 3190, 3324, 3531, 1330, -10837, -10628, -10953, -10732, -10741, -10629, -10837, -10882, -8458, 9556, 3868, 10958, 8406, -2679, 2772, -4939, -8986, 4118, 9209, 4368, 8935, -3893, -3341, -5088, -8424, 10938, 10154, 8782, -3113, 3540, 3969, 9652, 3128, 3588, 2241, -3095, 3465, 4298, 7744, -10122, -3217, -3260, 1618, -8655, 9991, 3694, 9342, -3939, -4346, -9323, 3592, 2089, -2850, 3401, 4025, 9585, 2978, 3667, 2457, -4470, -10804, -10868, -8183, 7922, -11041, -9392, -4742, -10772, -10702, -9353, 3395, 3027, 3532, 3227, 3251, 3245, 3231, 3410, 2519, -4548, -10687, -10808, -10903, -10695, -10741, -10645, -10853, -11081, -8317, 10820, 8143, -2491, 2775, -5083, -9254, 4432, 10331, 8289, -1819, 9009, -4278, -4592, -8453, 11023, 10206, 8582, -3859, -3381, -5124, -8995, 3876, 3080, 2242, -2918, 3521, 4333, 9528, 2866, 3705, 3472, 484, -7795, 9973, 3878, 8807, -4395, -2004, 763, -8997, 2842, -3345, 3771, 4396, 9538, 2916, 3767, 1732, -2924, 5236, 6323, -7787, 8061, -12050, -8977, -4735, -10991, -10880, -7696, 9899, 2750, 3738, 3190, 3273, 3290, 3278, 3192, 3205, 3545, 1274, -10887, -10585, -11000, -10746, -10748, -10730, -10731, -10756, -10917, -10039, -2734, 2469, -4653, -9292, 4175, 10439, 7887, -10621, -10363, -10370, -4725, -8829, 10736, 10189, 9184, -3697, -3660, -3093, 3388, 1694, -9183, 2662, -3388, 3478, 3867, 9753, 3220, 3549, 3154, 3313, 3860, 9665, 4089, 9060, -3694, -2711, 1825, -10617, -10570, -9954, 3094, 3831, 9827, 3353, 3358, 2578, -2269, 8115, -10293, -8943, 7909, -10138, -10076, -4619, -10488, -10661, -9931, 2971, 3160, 3460, 2978, -135, -195, -275, -233, -264, -273, -218, -179, -168, -207, -244, -220, -220, -223, -227, -256, -208, -254, -223, -283, -250, -279, -220, -265, -249, -110, -40, -112, -80, -106, -171, -218, -184, -195, -220, -228, -161, -145, -195, -209, -222, -224, -222, -150, -214, -96, -66, -611, -279, -1115, -7949, -1388, -282, -121, -130, -116, -155, -151, -142, -164, -214, -191, -213, -177, -136, -189, -217, -140, -187, -239]
packet_str_EQUiSatx50 = "EQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSatEQUiSat"
packet_output_EQUiSatx50 = [ord(c) for c in packet_str_EQUiSatx50]
real_packets_hex = [
    "574c39585a454fd7030020a1320f08e0e3555c03032855f0b2c3b3a0b22fdee2555d03032855f0b27d58c1c15555c155e3d303002fe1e1555f03032855f0b27d58c1c15555c15565d003002fe3de5a5503032855f0e17d58c1c15555c155dbcc03002fe1de5a5503032855f0e17d58c1c15455c1555dc903002fe1de5b5503032855f0e17d58c1c15455c155d3c503002fdfe0555803032855f0f27d58c1c15555c15554c203002fdfe1555803032855f0f27d58c1c1c1c1c1c1cdbe03000e02050e01059b2a069c1c009c1a009c1900263c06d64c069b2f000815069c300542270a737478524623cc2284a37b588967b5a8d6d8e6063f93f0d04c23ae3654",
    "574c39585a455319020021a5323b04dee3555c03032855f0b2c4b49fb300000000000000000000000079097c82c27c82c27f7f807678787678784616020000000000000000000000000079097c82c27c82c27f7f807678787678789611020000000000000000000000000079057c82c17c82c27f7f80767878767878e60c020000000000000000000000000079097c82c17c82c27f7f807678787678783608020000000000000000000000000079097c82c27c82c27f7f80767878767878860302009c30051c05051c02051c01059b29059b2905d64c059b2a0e9c1cff000000326466aa38edaa9523ab2ac822d84d5facd46b418f3978e88e468141ca2066",
	"574c39585a45f23304002297323c08dee3555b03032854f0b2c5b39fb203030303030303030303030303030403030303030303030203030303030303030303030303030303030301000200010001000100010002000100010002000100010001000100c5b1a0b2c6b2a1b1c6b29fb1c4b2a1b1c4b3a0b1c2b2a0b2c5b29db2161e071b2323141b232b050530300711191119112b210f21162111217f7f807f7f807f7f807f7f807f7f807f7f807f7f80f53304009b2f009c2eff9c30009b2f009c2e000815009c1fff9c1c009c20ff9c1bff9c1dff9c1eff9c19009c1f0000b5d38433b3764afbb6734b204e06f888445fbac94129af66accf0d74460e902d",
    "574c39585a45fac302002297323a07e2de5a5503032855f0e1c5b4a1b103030403030303030303030303030303030303030303030303030303030303030303030303030303030302000100010001000200010001000100010001000100010001000100c6b1a0b1c4b2a3b0c7b19eb1c3b29fb1c2b39eb3c6b1a2b0c4b39eb2050a0c1132260a19261e1b2316190f2116191419211911281b1911197f7f807f7f807f7f807f7f807f7f807f7f807f7f80fbc302000e06000e04000e03009c1aff9c19ff0e02000e01009c1cff9c19019c1fff9c20ff9c1bff9c1dff9c1eff0039a6aca520321ac66993d0219fa0c9c1bb0a752183d115979df53f83ba28c072"
]

class qa_equisat_4fsk_block_decode (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_decode_block(self):
        self.decode_test_helper(packet_raw_EQUiSatx50, 856, "tEQUiSatEQUiSatEQU")
        self.decode_test_helper(packet_raw_EQUiSatx50, 616, "QUiSatEQUiSatEQUiS")
        self.decode_test_helper(packet_raw_EQUiSatx50, 1496, "iSatEQUiSatEQUiSat")

    def decode_test_helper(self, inpt, start, str_expected):
        inpt_np = np.array(inpt[start:start + 80])
        syms = equisat_4fsk_preamble_detect.get_symbols(inpt_np, 9203, -9575)
        out = equisat_4fsk_block_decode.decode_block(syms)
        st = equisat_4fsk_block_decode._bytearr_to_string(out)
        self.assertEquals(st, str_expected)

    def test_full_packet(self):
        packets = self.full_test_helper(packet_raw_EQUiSatx50, 1, 350)
        self.assertEqual(len(packets), 1)
        self.assertFloatTuplesAlmostEqual(packet_output_EQUiSatx50, packets[0])

    def test_many_full_packets(self, ):
        data = self.read_wave("../samples/4fsk_data_tests/EQUiSatx50_all.wav") #  # 0to4_sweep_2_val
        packets = self.full_test_helper(data, 10, 350)
        self.assertEqual(len(packets), 12)
        for i in [0, 1, 2, 3, 4, 5, 7, 8, 9, 11]:
            self.assertFloatTuplesAlmostEqual(packet_output_EQUiSatx50, packets[i])

    def test_actual_packets(self, ):
        data = self.read_wave("../samples/4fsk_data_tests/4_equisat_packets_2nd_correct.wav")
        packets = self.full_test_helper(data, 3, 255)

        # print(real_packets_hex[3])
        # print(binascii.hexlify(bytearray(packets[2])))
        # self.num_diff(real_packets_hex[1], binascii.hexlify(bytearray(packets[1])))

        self.assertEqual(len(packets), 4)
        self.assertFloatTuplesAlmostEqual(bytearray.fromhex(real_packets_hex[1]), packets[1])
        # self.assertFloatTuplesAlmostEqual(bytearray.fromhex(real_packets_hex[2]), packets[2])

    def full_test_helper(self, data, num_packets, num_bytes):
        src = blocks.vector_source_f(data, repeat=False)
        preamble_detector = equisat_4fsk_preamble_detect(byte_buf_size=num_bytes)
        block_decoder = equisat_4fsk_block_decode(msg_size=num_bytes)
        dst = blocks.message_debug()
        self.tb.connect(src, preamble_detector)
        self.tb.msg_connect(preamble_detector, "out", block_decoder, "in")
        self.tb.msg_connect(block_decoder, "out", dst, "store")

        # Wait for all messages to be sent
        self.tb.start()
        while block_decoder.num_packets < num_packets:
            time.sleep(1.5)
        self.tb.stop()
        self.tb.wait()

        # may be more packets received than num_packets
        packets = []
        for i in range(dst.num_messages()):
            packets.append(pmt.u8vector_elements(pmt.cdr(dst.get_message(i))))
        return packets

    @staticmethod
    def read_wave(fname):
        _, adata = wavfile.read(fname)
        return adata.tolist()

    @staticmethod
    def num_diff(expected, real):
        assert len(expected) == len(real)
        total = 0
        for i in range(len(expected)):
            if expected[i] != real[i]:
                print("i: %s vs. %s" % (expected[i], real[i]))
                total += 1
        print(total)
        return total

if __name__ == '__main__':
    gr_unittest.run(qa_equisat_4fsk_block_decode, "qa_equisat_4fsk_block_decode.xml")
