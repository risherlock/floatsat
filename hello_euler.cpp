// Euler angles from LSM9DS1 IMU

#include "rodos.h"
#include "lsm9ds1.h"

#define D2R 0.01745329251f
#define R2D 57.2957795131f

class HelloEuler : public StaticThread<>
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

      float ypr[3] = {0.0};
      ypr[0] = lsm9ds1_get_heading(m, a);
      ypr[1] = lsm9ds1_get_pitch(a);
      ypr[2] = lsm9ds1_get_roll(a);
      PRINTF("%f, %f, %f\r\n", ypr[0] * R2D, ypr[1] * R2D, ypr[2] * R2D);
    }
  }

} hello_euler;
