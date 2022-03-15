#include <RGBmatrixPanel.h>

#define CLK 11 // USE THIS ON ARDUINO MEGA
#define OE   9
#define LAT 10
#define A   A0
#define B   A1
#define C   A2
#define D   A3
RGBmatrixPanel matrix(A, B, C, D, CLK, LAT, OE, false);

int8_t ball[3][4] = {
  {  3,  0,  1,  1 }, // Initial X,Y pos & velocity for 3 bouncy balls
  { 0, 27,  1, -1 },
  { 20,  9, -1,  -1 }
};
static const uint16_t PROGMEM ballcolor[3] = {
  0xFFFF, // Green=1
  0x001F, // Blue=1
  0xF800  // Red=1
};

void setup() {
  matrix.begin();
}

void loop() {
  byte i;

  matrix.fillScreen(0); // Clears screen
 
  // Bounce three balls around
  for(i=0; i<1; i++) {
    // Draw 'ball'
    matrix.fillCircle(ball[i][0], ball[i][1], 4, pgm_read_word(&ballcolor[i]));
    // Update X, Y position
    ball[i][0] += ball[i][2];
    ball[i][1] += ball[i][3];
    // Bounce off edges
    if((ball[i][0] == 0) || (ball[i][0] == (matrix.width() - 1)))
      ball[i][2] *= -1;
    if((ball[i][1] == 0) || (ball[i][1] == (matrix.height() - 1)))
      ball[i][3] *= -1;
  }
  
#if !defined(__AVR__)
  // On non-AVR boards, delay slightly so screen updates aren't too quick.
  delay(20);
#endif

  // Update display
  matrix.swapBuffers(false);
}
