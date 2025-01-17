// Raw accelerometer and gyroscope measurements form LSM9DS1

#include "rodos.h"
#include "VL53L4ED_api.h"

#define D2R 0.01745329251f
#define R2D 57.2957795131f

#define TOF_I2C_ADDRESS 0x29

VL53L4ED_ResultsData_t tof_result;

class HelloTOF : public StaticThread<>
{
  void init()
  {

    // Initialize and return status
    if (VL53L4ED_SensorInit(TOF_I2C_ADDRESS) == VL53L4ED_ERROR_NONE)
    {
      // Enable 10 ms sampling and start sampling
      VL53L4ED_SetRangeTiming(TOF_I2C_ADDRESS, 10, 0);
      VL53L4ED_StartRanging(TOF_I2C_ADDRESS);
      PRINTF("\r\nTOF success!\r\n");
    }
    else
    {
      PRINTF("\r\nTOF error!\r\n");
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
    }
  }

} hello_tof;
