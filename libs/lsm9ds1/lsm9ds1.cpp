//  Rishav (2023-11-04)

#include <cmath>
#include "lsm9ds1.h"
#include "lsm9ds1_settings.h"

/*
  Each sensor must be configured to match these resolutions.
  Please consult register mapping on the datasheet for custom configuration.
*/
#define LSM9DS1_ACCEL_g_PER_LSB LSM9DS1_ACCEL_mg_LSB_2G / 1000.0F
#define LSM9DS1_GYRO_RPS_PER_LSB LSM9DS1_GYRO_DPS_DIGIT_2000DPS *(M_PI / 180.0F)
#define LSM9DS1_MAG_uT_PER_LSB LSM9DS1_MAG_mG_4GAUSS / 10.0

bool check_i2c(void);
void init_gyro(void);
void init_accel(void);
void init_mag(void);

// SCL-PB10, SDA-PB11
HAL_I2C IMU(I2C_IDX2);

// Initialize and check LSM9DS1
bool lsm9ds1_init(void)
{
  const int i2c_freq = 400000;
  IMU.init(i2c_freq);

  if (check_i2c())
  {
    init_gyro();
    init_accel();
    init_mag();

    return true;
  }

  return false;
}

// Is it LSM9DS1?
bool check_i2c(void)
{
  uint8_t rx_gyro_id[1] = {0};
  uint8_t rx_accel_mag_id[1] = {0};

  IMU.writeRead(LSM9DS1_ADDR_AG, &LSM9DS1_WHO_AM_I, 1, rx_gyro_id, 1);
  IMU.writeRead(LSM9DS1_ADDR_M, &LSM9DS1_WHO_AM_I, 1, rx_accel_mag_id, 1);

  if ((rx_gyro_id[0] == LSM9DS1_G_RESPONSE) && (rx_accel_mag_id[0] == LSM9DS1_XM_RESPONSE))
  {
    return true;
  }
  else
  {
    return false;
  }
}

// Configure gyroscope
void init_gyro(void)
{
  const uint8_t ctrl_reg1_g_setting[] = {LSM9DS1_CTRL_REG1_G, 0b0111111};
  IMU.write(LSM9DS1_ADDR_AG, ctrl_reg1_g_setting, 2);
}

// Configure accelerometer
void init_accel(void)
{
  const uint8_t ctrl_reg6_xl_setting[] = {LSM9DS1_CTRL_REG6_XL, 0b01100000};
  IMU.write(LSM9DS1_ADDR_AG, ctrl_reg6_xl_setting, 2);
}

// Configure magnetometer
void init_mag(void)
{
  const uint8_t ctrl_reg1_m_setting[] = {LSM9DS1_CTRL_REG1_M, 0b10111110};
  const uint8_t ctrl_reg2_m_setting[] = {LSM9DS1_CTRL_REG2_M, 0b00000000};
  const uint8_t ctrl_reg3_m_setting[] = {LSM9DS1_CTRL_REG3_M, 0b00000000};

  IMU.write(LSM9DS1_ADDR_M, ctrl_reg1_m_setting, 2);
  IMU.write(LSM9DS1_ADDR_M, ctrl_reg2_m_setting, 2);
  IMU.write(LSM9DS1_ADDR_M, ctrl_reg3_m_setting, 2);
}

// Acceleration in number of g's
bool lsm9ds1_read_accel(float a[3])
{
  uint8_t data[6];
  int status = IMU.writeRead(LSM9DS1_ADDR_AG, &LSM9DS1_OUT_X_L_XL, 1, data, 6);

  a[0] = ((int16_t)(data[1] << 8) | data[0]) * LSM9DS1_ACCEL_g_PER_LSB;
  a[1] = ((int16_t)(data[3] << 8) | data[2]) * LSM9DS1_ACCEL_g_PER_LSB;
  a[2] = ((int16_t)(data[5] << 8) | data[4]) * LSM9DS1_ACCEL_g_PER_LSB;

  return !(status < 0);
}

// Angular velocity in rad/s
bool lsm9ds1_read_gyro(float g[3])
{
  uint8_t data[6] = {0, 0, 0, 0, 0, 0};
  int status = IMU.writeRead(LSM9DS1_ADDR_AG, &LSM9DS1_OUT_X_L_G, 1, data, 6);

  g[0] = ((int16_t)(data[1] << 8) | data[0]) * LSM9DS1_GYRO_RPS_PER_LSB;
  g[1] = ((int16_t)(data[3] << 8) | data[2]) * LSM9DS1_GYRO_RPS_PER_LSB;
  g[2] = ((int16_t)(data[5] << 8) | data[4]) * LSM9DS1_GYRO_RPS_PER_LSB;

  return !(status < 0);
}

// Sign of input number
double sign(const double in)
{
  if (in < 0)
  {
    return -1;
  }
  else
  {
    return 1;
  }
}

// Magnetic field intensity in uT
bool lsm9ds1_read_mag(float m[3])
{
  uint8_t data[6];
  int status = IMU.writeRead(LSM9DS1_ADDR_M, &LSM9DS1_OUT_X_L_M, 1, data, 6);

  m[0] = ((int16_t)(data[1] << 8) | data[0]) * LSM9DS1_MAG_uT_PER_LSB;
  m[1] = ((int16_t)(data[3] << 8) | data[2]) * LSM9DS1_MAG_uT_PER_LSB;
  m[2] = ((int16_t)(data[5] << 8) | data[4]) * LSM9DS1_MAG_uT_PER_LSB;

  return !(status < 0);
}

// Rotation about X-axis in radians
float lsm9ds1_get_roll(const float a[3])
{
  return atan2(a[1], sign(a[2]) * sqrt(a[0] * a[0] + a[2] * a[2]));
}

// Rotation about Y-axis in radians
float lsm9ds1_get_pitch(const float a[3])
{
  return atan2(-a[0], sqrt(a[1] * a[1] + a[2] * a[2]));
}

// Tilt compensated yaw in radians
float lsm9ds1_get_heading(const float m[3], const float a[3])
{
  const float roll = atan2(a[1], sign(a[2]) * sqrt(a[0] * a[0] + a[2] * a[2]));
  const float pitch = atan2(-a[0], sqrt(a[1] * a[1] + a[2] * a[2]));

  // Tilt compensation matrix
  float dcm[3][3] = {0.0f};
  const float cp = cos(pitch);
  const float cr = cos(roll);
  const float sp = sin(pitch);
  const float sr = sin(roll);

  dcm[0][0] = cp;
  dcm[1][0] = sr * sp;
  dcm[2][0] = cr * sp;
  dcm[0][1] = 0;
  dcm[1][1] = cr;
  dcm[2][1] = -sr;
  dcm[0][2] = -sp;
  dcm[1][2] = sr * cp;
  dcm[2][2] = cr * cp;

  // Tilt compensation
  float m_hat[3] = {0.0};
  for (uint8_t r = 0; r < 3; r++)
  {
    float elem = 0.0;
    for (uint8_t c = 0; c < 3; c++)
    {
      elem += dcm[r][c] * m[c];
    }
    m_hat[r] = elem;
  }

  // [-pi, pi]
  float psi = atan2(m_hat[1], m_hat[0]);

  // [0, 2*pi]
  psi += M_PI;
  while (psi < 0)
  {
    psi += M_PI;
  }

  return psi;
}

// m_hat = Ainv * (m - b)
void magcal(float m[3], const float Ainv[3][3], const float b[3])
{
  float m_hat[3] = {0.0};

  for (uint8_t r = 0; r < 3; r++)
  {
    float temp = 0.0;
    for (uint8_t c = 0; c < 3; c++)
    {
      temp += Ainv[r][c] * (m[c] - b[c]);
    }
    m_hat[r] = temp;
  }

  m[0] = m_hat[0];
  m[1] = m_hat[1];
  m[2] = m_hat[2];
}
