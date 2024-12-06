// Raw accelerometer and gyroscope measurements form LSM9DS1

#include "rodos.h"
#include "lsm9ds1.h"

#define D2R 0.01745329251f
#define R2D 57.2957795131f

class HelloIMU : public StaticThread<>
{
  void init()
  {
    if (lsm9ds1_init())
    {
      PRINTF("\r\nSuccessful initialization!\r\n");
    }
    else
    {
      PRINTF("\r\nIMU error!\r\n");
      while (1)
      {
      }
    }
  }

  void run()
  {
    init();

    TIME_LOOP(100 * MILLISECONDS, 100 * MILLISECONDS)
    {
      float a[3], g[3], m[3];
      if (!(lsm9ds1_read_accel(a) && lsm9ds1_read_gyro(g) && lsm9ds1_read_mag(m)))
      {
        lsm9ds1_init();
      }

      PRINTF("a-xyz: %f, %f, %f  g-xyz: %f, %f, %f\r\n", a[0], a[1], a[2], g[0], g[1], g[2]);
    }
  }

} hello_imu;
