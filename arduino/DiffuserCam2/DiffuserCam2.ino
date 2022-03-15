#include <RGBmatrixPanel.h>

#define CLK 11 // USE THIS ON ARDUINO MEGA
#define OE   9
#define LAT 10
#define A   A0
#define B   A1
#define C   A2
#define D   A3
RGBmatrixPanel matrix(A, B, C, D, CLK, LAT, OE, false);
const char str[] PROGMEM = "CALCAL";
int16_t textX     = matrix.width(),
        textMin   = (int16_t)sizeof(str) * -12,
        hue       = 0;

void setup() {
  matrix.begin();
  matrix.setTextWrap(false);
  matrix.setTextSize(1);
}

void loop() {
  matrix.fillScreen(0);
  matrix.setTextColor(matrix.Color333(7, 7, 7));
  //matrix.setTextColor(matrix.ColorHSV(hue, 255, 255, true));
  matrix.setCursor(textX, 1);
  //matrix.setCursor(0, 1);
  matrix.print("CALCALCALCALCALCALCALCALCAL");
  if((--textX) < textMin) textX = matrix.width();
  hue += 7;
  if(hue >= 1536) hue -= 1536;
#if !defined(__AVR__)
  // On non-AVR boards, delay slightly so screen updates aren't too quick.
  delay(20);
#endif
  
  // Update display
  matrix.swapBuffers(false);
}
