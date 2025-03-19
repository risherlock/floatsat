// Test file for VL53L4ED ToF sensor with (or without) median filter

#include "rodos.h"
#include "MedianFilter.h"
#include "VL53L4ED_api.h"

#define TOF_I2C_ADDRESS 0x29

// true enables median filter
bool tof_filter_flag = false;
static MedianFilter<int, 25> filter;

class HelloTOF : public StaticThread<>
{
  void init()
  {
    tof_i2c_init();

    // Initialize and return status
    if (VL53L4ED_SensorInit(TOF_I2C_ADDRESS) == VL53L4ED_ERROR_NONE)
    {
      // Enable 10 ms sampling and start sampling
      VL53L4ED_SetRangeTiming(TOF_I2C_ADDRESS, 10, 0);
      VL53L4ED_StartRanging(TOF_I2C_ADDRESS);
      PRINTF("\r\nToF initialized!\r\n");
    }
    else
    {
      PRINTF("\r\nToF error!\r\n");
      while (1)
      {
      }
    }
  }

  void run()
  {
    init();

    // A guide to using the VL53L4CD ultra lite driver (UM2931): Figure 7
    TIME_LOOP(100 * MILLISECONDS, 500 * MILLISECONDS)
    {
      uint8_t data_ready = 0;
      int distance = 0;

      VL53L4ED_ResultsData_t tof_result;

      // Wait for data to be ready
      if (data_ready != (uint8_t)1)
      {
        VL53L4ED_CheckForDataReady(TOF_I2C_ADDRESS, &data_ready);
      }

      // Read distance measurements
      if (VL53L4ED_GetResult(TOF_I2C_ADDRESS, &tof_result) == VL53L4ED_ERROR_NONE)
      {
        if (tof_filter_flag)
        {
          filter.addSample(tof_result.distance_mm);
          distance = filter.getMedian();
        }
        else
        {
          distance = tof_result.distance_mm;
        }

        PRINTF("Distance: %d mm\n", distance);
        VL53L4ED_ClearInterrupt(TOF_I2C_ADDRESS);
      }
      else
      {
        PRINTF("ToF ranging error!\n");
      }
    }
  }

} hello_tof;
