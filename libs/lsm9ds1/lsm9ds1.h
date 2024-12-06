#ifndef _LSM9DS0_H_
#define _LSM9DS0_H_

#include "rodos.h"
#include "hal.h"

bool lsm9ds1_init(void);
bool lsm9ds1_read_gyro(float a[3]);
bool lsm9ds1_read_mag(float a[3]);
bool lsm9ds1_read_accel(float a[3]);

float lsm9ds1_get_roll(const float a[3]);
float lsm9ds1_get_pitch(const float a[3]);
float lsm9ds1_get_heading(const float m[3], const float a[3]);

void magcal(float m[3], const float Ainv[3][3], const float b[3]);

#endif // lsm9ds1.h
