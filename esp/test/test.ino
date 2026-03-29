// پین‌ها
const int trigPin = 9;
const int echoPin = 10;

// متغیر فاصله
long duration;
float distanceCm;

void setup() {
  // پین‌ها را تنظیم می‌کنیم
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  Serial.begin(9600);
}

void loop() {
  // سیگنال trigger را تمیز می‌کنیم
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  // ارسال پالس
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // دریافت پالس از echo
  duration = pulseIn(echoPin, HIGH);

  // محاسبه فاصله (سرعت صوت ~ 343 متر بر ثانیه)
  // فاصله = (زمان * سرعت صوت) / 2
  distanceCm = (duration * 0.0343) / 2;

  // چاپ نتیجه
  Serial.print("Distance: ");
  Serial.print(distanceCm);
  Serial.println(" cm");

  delay(200);
}
