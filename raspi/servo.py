from gpiozero import Button, PWMOutputDevice 
import threading 
 
class Servo: 
    def __init__(self): 
        # エンコーダの設定（GPIOピンの割り当て） 
        self.ENC_R = Button(10, pull_up=True)  # 右側エンコーダ 
        self.ENC_L = Button(2, pull_up=True)   # 左側エンコーダ 
        self.count_R = 0  # 右側のパルスカウント 
        self.count_L = 0  # 左側のパルスカウント 
 
        # エンコーダのイベントにコールバック関数を登録 
        self.ENC_R.when_pressed = self.enc_callback_R 
        self.ENC_R.when_released = self.enc_callback_R 
        self.ENC_L.when_pressed = self.enc_callback_L 
        self.ENC_L.when_released = self.enc_callback_L 
 
        # モーターのPWM出力の設定 
        self.MOT_R_1 = PWMOutputDevice(pin=23, frequency=60) 
        self.MOT_R_2 = PWMOutputDevice(pin=22, frequency=60) 
        self.MOT_L_1 = PWMOutputDevice(pin=27, frequency=60) 
        self.MOT_L_2 = PWMOutputDevice(pin=17, frequency=60) 
 
        # PID制御のパラメータ初期化 
        self.DURATION = 0.1  # 制御周期（秒） 
        self.prev_count_R = 0 
        self.prev_count_L = 0 
        self.err_prev_R = 0 
        self.err_prev_L = 0 
        self.err_I_R = 0 
        self.err_I_L = 0 
        self.Kp = 20      # 比例ゲイン 
        self.Ki = 100     # 積分ゲイン 
        self.Kd = 0.1     # 微分ゲイン 
        self.target_speed_R = 0  # 右モーターの目標速度 
        self.target_speed_L = 0  # 左モーターの目標速度
        self.target_count_L = 0  # 目標左エンコーダカウント
        self.target_count_R = 0  # 目標右エンコーダカウント
 
    # 右エンコーダのコールバック関数 
    def enc_callback_R(self): 
        if self.target_speed_R > 0: 
            self.count_R += 1 
        elif self.target_speed_R < 0: 
            self.count_R -= 1 
        #print('R= ' + str(self.count_R)) #画面出力
 
    # 左エンコーダのコールバック関数 
    def enc_callback_L(self): 
        if self.target_speed_L > 0: 
            self.count_L += 1 
        elif self.target_speed_L < 0: 
            self.count_L -= 1
        #print('L= ' + str(self.count_L)) #画面出力 
 
    # 右モーター用の変数初期化 
    def init_variables_R(self): 
        self.count_R = 0 
        self.prev_count_R = 0 
        self.err_prev_R = 0 
        self.err_I_R = 0 
        self.MOT_R_1.value = 0 
        self.MOT_R_2.value = 0 
     
    # 左モーター用の変数初期化 
    def init_variables_L(self): 
        self.count_L = 0 
        self.prev_count_L = 0 
        self.err_prev_L = 0 
        self.err_I_L = 0 
        self.MOT_L_1.value = 0 
        self.MOT_L_2.value = 0 
 
    # PID制御によるモーター駆動 
    def drive(self):
        #self.target_count_L = 50
        #self.target_count_R = -50
        # --- 右モーターのPID制御 --- 
        speed_R = (self.count_R - self.prev_count_R) / 40 / self.DURATION  # 速度計算 
        err_P = self.target_speed_R - speed_R  # 比例誤差 
        self.err_I_R += err_P * self.DURATION  # 積分誤差の更新 
        err_D = (err_P - self.err_prev_R) / self.DURATION  # 微分誤差 
        duty_R = self.Kp * err_P + self.Ki * self.err_I_R + self.Kd * err_D  # PID出力 
 
        # PWM出力のクリッピング（範囲制限） 
        duty_R = max(min(duty_R, 100.0), -100.0) 
 
        # PWM出力の設定（正転 or 逆転） 
        if duty_R > 0: 
            self.MOT_R_1.value = duty_R / 100.0 
            self.MOT_R_2.value = 0 
        else: 
            self.MOT_R_1.value = 0 
            self.MOT_R_2.value = -duty_R / 100.0 
 
        self.prev_count_R = self.count_R 
        self.err_prev_R = err_P 
 
        # --- 左モーターのPID制御 --- 
        speed_L = (self.count_L - self.prev_count_L) / 40 / self.DURATION 
        err_P = self.target_speed_L - speed_L 
        self.err_I_L += err_P * self.DURATION 
        err_D = (err_P - self.err_prev_L) / self.DURATION 
        duty_L = self.Kp * err_P + self.Ki * self.err_I_L + self.Kd * err_D 
 
        duty_L = max(min(duty_L, 100.0), -100.0) 
 
        if duty_L > 0: 
            self.MOT_L_1.value = duty_L / 100.0 
            self.MOT_L_2.value = 0 
        else: 
            self.MOT_L_1.value = 0 
            self.MOT_L_2.value = -duty_L / 100.0 
 
        self.prev_count_L = self.count_L 
        self.err_prev_L = err_P 
 
        # 到達チェック
        if abs(self.count_L) > abs(self.target_count_L):
            self.target_speed_L = 0
        if abs(self.count_R) > abs(self.target_count_R):
            self.target_speed_R = 0
        if self.target_speed_L == 0 and self.target_speed_R == 0:
            self.set_speed(0, 0)
            self._caller.is_moving = False
            return
        else:
            # 次回の制御呼び出しをスケジュール（一定周期） 
            t = threading.Timer(self.DURATION, self.drive) 
            t.start() 
 
    # 目標速度の設定 
    def set_speed(self, speed_L, speed_R): 
        self.target_speed_L = speed_L 
        if self.target_speed_L == 0: 
            self.init_variables_L()  # 停止時は変数をリセット 
 
        self.target_speed_R = speed_R 
        if self.target_speed_R == 0: 
            self.init_variables_R()

    # 有期動作
    def action(self, caller, type, ang, dist):
        
        self._caller = caller
        if type == "forward":
            self.target_count_L = dist * 40 / (7 * 3.14)
            self.target_count_R = self.target_count_L
            self.set_speed(0.5, 0.5)
        elif type == "back":
            self.target_count_L = -dist * 40 / (7 * 3.14)
            self.target_count_R = self.target_count_L
            self.set_speed(-0.5, -0.5)
        elif type == "left":
            self.target_count_L = -ang * 13 * 3.14 * 40 / 360 / (7 * 3.14)
            self.target_count_R = -self.target_count_L
            self.set_speed(-0.5, 0.5)
        elif type == "right":
            self.target_count_L = ang * 13 * 3.14 * 40 / 360 / (7 * 3.14)
            self.target_count_R = -self.target_count_L
            self.set_speed(0.5, -0.5)
        else:
            self.set_speed(0,0)
        self.init_variables_L()
        self.init_variables_R()
        self.drive()
 
# メイン関数 
def main(): 
    servo = Servo()
    
    servo.action(main,"right", 5)  # 最初の制御呼び出し 
 
    try: 
        while True: 
            pass  # 無限ループで動作を維持 
    except KeyboardInterrupt: 
        # キーボード割り込み（Ctrl+C）時にモーターを停止 
        servo.MOT_R_1.value = 0 
        servo.MOT_R_2.value = 0 
        servo.MOT_L_1.value = 0 
        servo.MOT_L_2.value = 0 
 
# プログラム実行エントリポイント 
if __name__ == "__main__": 
    main()