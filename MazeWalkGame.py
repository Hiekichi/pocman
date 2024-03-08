import pyxel

class App():
    def __init__(self):
        pyxel.init(168,128,title="ぱっくまん風味",fps=24)
        pyxel.load("pocman.pyxres")
        self.is_gaming = True
        self.KEY = [pyxel.KEY_UP,pyxel.KEY_RIGHT,pyxel.KEY_DOWN,pyxel.KEY_LEFT]
        self.D = [[0,0],[0,-1],[1,0],[0,1],[-1,0]]
        self.high_score = 0
        self.score = 0
        self.init_stage()
        pyxel.run(self.update,self.draw)

    def init_stage(self):
        self.counter = 0
        if self.score > self.high_score:
            self.high_score = self.score
        self.score = 0
        self.my_pos = [8*8,8*12]
        self.my_dir = 0
        self.mons = [[8*7,8*8],[8*7,8*8],[8*8,8*8],[8*8,8*8]]
        self.mons_dir = [4, 4, 2, 2]
        self.mons_active = [True,True,True,True]
        self.power_count = 0  # パワーエサ用
        self.power_add_count = 0  # 齧ったの何匹目？
        self.power_add_SCORE = [100,200,400,800]
        self.power_add_pos = []
        self.eat_cnt = 0
        self.is_clear = False
        self.init_tilemap()

    def init_tilemap(self):
        for y in range(16):
            for x in range(16):
                if pyxel.tilemaps[0].pget(x,y) == (2,0):
                    pyxel.tilemaps[0].pset(x,y,(0,1))
                elif pyxel.tilemaps[0].pget(x,y) == (3,0):
                    pyxel.tilemaps[0].pset(x,y,(1,1))

    def update(self):
        ### 独自のframeカウンター
        self.counter += 1

        ### ステージクリアしていたら
        if self.is_clear:
            return

        ### ステージクリアしたかの確認
        if self.eat_cnt > 117:
            self.is_clear = True
            self.is_gaming = False
            self.counter = 0

        ### 自分と敵の当たり判定 　※ゲームオーバー or パワークッキーで齧る
        for i in range(4):
            dx = abs(self.my_pos[0] - self.mons[i][0])
            dy = abs(self.my_pos[1] - self.mons[i][1])
            if dx < 6 and dy < 6:
                if self.power_count > 0: # パワークッキー中に敵と接触
                    if self.mons_active[i]:
                        self.score += self.power_add_SCORE[self.power_add_count] # 加点処理
                        self.power_add_pos.append([self.mons[i][0],self.mons[i][1]])
                        self.power_add_count += 1
                        self.mons[i] = [8*(8-(i%2)),8*8]
                        self.mons_active[i] = False
                else: # パワークッキー中じゃなくて敵と接触したら
                    self.is_gaming = False

        ### 敵キャラの移動
        for i in range(4):
            if self.mons_active[i]: ## モンスターがアクティブで、
                if self.mons[i][0]%8==0 and self.mons[i][1]%8==0: #マス目上
                    self.teki_change_move(i)
                else: #マスの間を移動中
                    self.mons[i][0] += (self.D[self.mons_dir[i]][0] * 1)
                    self.mons[i][1] += (self.D[self.mons_dir[i]][1] * 1)

        ### ゲームオーバーしていたら
        if not self.is_gaming:
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.is_gaming = True
                self.init_stage()
            return

        ### パワークッキーのカウントダウン
        if self.power_count > 0:
            self.power_count -= 1
            if self.power_count <= 0:
                self.mons_active = [True,True,True,True]
                self.power_add_count = 0
                self.power_add_pos = []
                self.counter = 0


        ### 自キャラの移動とクッキー食べる処理
        if self.my_pos[0]%8==0 and self.my_pos[1]%8==0:
            cx = int(self.my_pos[0]/8)
            cy = int(self.my_pos[1]/8)
            
            tmp_dir = self.my_dir
            for i in range(4):
                if pyxel.btn(self.KEY[i]):
                    tmp_dir = i + 1
            
            tmpnx = cx + self.D[tmp_dir][0]
            tmpny = cy + self.D[tmp_dir][1]
            tmptpl = pyxel.tilemaps[0].pget(tmpnx,tmpny)
            if tmp_dir != 0 and tmptpl == (1,0): # 向きを変えようとしたけど壁だった
                nx = cx + self.D[self.my_dir][0]
                ny = cy + self.D[self.my_dir][1]
                tpl = pyxel.tilemaps[0].pget(nx,ny)
                if tpl == (1,0): # さらに今の方向も壁だったならば
                    self.my_dir = 0 # 停止せよ、壁以外だったらそのまま進みなさい
                self.my_pos[0] += (self.D[self.my_dir][0] * 2)
                self.my_pos[1] += (self.D[self.my_dir][1] * 2)
            else:
                self.my_dir = tmp_dir
                nx = cx + self.D[self.my_dir][0]
                ny = cy + self.D[self.my_dir][1]
                tpl = pyxel.tilemaps[0].pget(nx,ny)
                if tpl == (1,0): # 進行方向が壁だったら
                    self.my_dir = 0 # 停止
                if tpl == (0,1): # 進行方向がクッキーだったら
                    self.score += 1 # 1点追加
                    self.eat_cnt += 1 #食べた数を1増やす
                    pyxel.tilemaps[0].pset(nx,ny,(2,0)) # 通路に変える
                elif tpl == (1,1): # 進行方向がパワークッキーだったら
                    self.score += 5 # 5点追加
                    self.eat_cnt += 1 #食べた数を1増やす
                    self.power_count = 120 # パワーアップ中にする
                    pyxel.tilemaps[0].pset(nx,ny,(3,0)) # 通路に変える
                    self.power_add_count = 0
                    self.power_add_pos = []
                    self.mons_active = [True,True,True,True]

                self.my_pos[0] += (self.D[self.my_dir][0] * 2)
                self.my_pos[1] += (self.D[self.my_dir][1] * 2)
        else:
            self.my_pos[0] += (self.D[self.my_dir][0] * 2)
            self.my_pos[1] += (self.D[self.my_dir][1] * 2)


    def draw_stage_clear_demo(self):
        if self.counter < 24:
            pyxel.circ(self.my_pos[0],self.my_pos[1],self.counter*4,self.counter%16)
        elif self.counter < 48:
            pyxel.cls(0)
        elif self.counter == 48:
            self.p_x = 128
            self.m_x = 153
        elif self.counter < 220:
            pyxel.cls(0)
            pyxel.blt(self.p_x,56,0,self.counter%2*8,40,8,8,0)
            pyxel.blt(self.m_x,56,0,8,48,8,8,0)
            self.p_x -= 0.9
            self.m_x -= 1
        elif self.counter == 220:
            self.p_x = -150
            self.m_x = -8
        elif self.counter < 440:
            pyxel.cls(0)
            pyxel.blt(self.m_x,56,0,0,80,8,8,0)
            pyxel.blt(self.p_x,48,0,self.counter%2*16,136,16,16,0)
            self.m_x += 1
            self.p_x += 1.7
        else:
            self.is_clear = False
            self.is_gaming = False
            self.counter = 0
            self.eat_cnt = 0

    def draw(self):
        ### ステージクリアしていたらデモ画面（インターミッション）を表示します
        if self.is_clear:
            self.draw_stage_clear_demo()
            return

        ### 画面全体を黒塗り
        pyxel.cls(0)
        ### マップを描画
        pyxel.bltm(0,0,0,0,0,128,128)
        ### ハイスコアとスコアを表示
        pyxel.text(132, 8,"Hi-Score",13)
        pyxel.text(132,16,"{}".format(self.high_score).rjust(8),7)
        pyxel.text(132,28,"   Score",13)
        pyxel.text(132,36,"{}".format(self.score).rjust(8),7)
        # 敵キャラ紹介
        pyxel.text(130,56,"  OIKAKE",13)
        pyxel.blt(154,62,0,0,48,8,8,0)
        pyxel.text(132,72,"MATIBUSE",13)
        pyxel.blt(154,78,0,0,56,8,8,0)
        pyxel.text(132,88,"KIMAGURE",13)
        pyxel.blt(154,94,0,0,64,8,8,0)
        pyxel.text(132,104,"OTOBOKE",13)
        pyxel.blt(154,110,0,0,72,8,8,0)
        ### 敵キャラを描画
        for i,m in enumerate(self.mons):
            if self.power_count > 0:  #パワークッキー中
                if self.power_count > 48:
                    pyxel.blt(m[0],m[1],0,0,80,8,8,0)
                else:
                    pyxel.blt(m[0],m[1],0,pyxel.frame_count%6*8,80,8,8,0)
            elif self.mons_dir[i] > 2: # 左向き
                pyxel.blt(m[0],m[1],0,8,48+8*i,8,8,0)
            else: # 右向き
                pyxel.blt(m[0],m[1],0,0,48+8*i,8,8,0)
        ### ゲームオーバーならメッセージを描画してreturn
        if not self.is_gaming:
            pyxel.text(48,56,"GAME OVER",pyxel.frame_count%16)
            pyxel.text(32,72,"ENTER TO RESTART",pyxel.frame_count%16)
            return
        ### 自キャラを描画
        if self.my_dir == 0:
            pyxel.blt(self.my_pos[0],self.my_pos[1],0,0,16,8,8,0)
        else:
            pyxel.blt(self.my_pos[0],self.my_pos[1],0,(pyxel.frame_count%2)*8,8+self.my_dir*8,8,8,0)
            pyxel.play(0,0)

        ### 敵がイジケ中なら点数表示
        if self.power_count > 0:
            for i,lst in enumerate(self.power_add_pos):
                pyxel.blt(lst[0],lst[1],0,i*16,88,16,8,0)

    def teki_change_move(self,i):
        ###### 目標地点（tx, ty）を求める 
        ### 赤（おいかけ）
        if i == 0:
            if (self.counter % 750) < 100:  # 縄張りに移動
                tx = ( 13  + pyxel.rndi(-2,2) ) * 8
                ty = (  2  + pyxel.rndi(-2,2) ) * 8
            else: # 自キャラを目標地点にする
                tx = self.my_pos[0]
                ty = self.my_pos[1]

        ### ピンク（まちぶせ）
        elif i == 1:
            if (self.counter % 750) < 150:  # 縄張りに移動
                tx = (  2  + pyxel.rndi(-2,2) ) * 8
                ty = (  2  + pyxel.rndi(-2,2) ) * 8
            else: # 自キャラの数歩先を目標地点にする
                tx = self.my_pos[0] + (self.D[self.my_dir][0] * 24)
                ty = self.my_pos[1] + (self.D[self.my_dir][1] * 24)

        ### 青（きまぐれ）
        elif i == 2:
            if (self.counter % 750) < 150: # 縄張りに移動
                tx = ( 13  + pyxel.rndi(-2,2) ) * 8
                ty = ( 13  + pyxel.rndi(-2,2) ) * 8
            else: # 自キャラを中心にオイカケの点対象の位置を目標地点にする
                tx = self.my_pos[0] + (self.my_pos[0] - self.mons[0][0])
                ty = self.my_pos[1] + (self.my_pos[1] - self.mons[0][1])

        ### オレンジ（おとぼけ）
        elif i == 3:
            if (self.counter % 750) < 150:  # 縄張りに移動
                tx = (  2  + pyxel.rndi(-2,2) ) * 8
                ty = ( 13  + pyxel.rndi(-2,2) ) * 8
            else: # 遠いときは追いかけ、近いときは逃げ、それ以外はランダムに
                dx = abs(self.my_pos[0] - self.mons[i][0])
                dy = abs(self.my_pos[1] - self.mons[i][1])
                if dx > 32 and dy > 32: # 遠いときは自キャラを目標地点にする
                    tx = self.my_pos[0]
                    ty = self.my_pos[1]
                elif dx < 16 and dy < 16: # 近いときは逃げる
                    tx = self.my_pos[0] - (self.my_pos[0] - self.mons[3][0])
                    ty = self.my_pos[1] - (self.my_pos[1] - self.mons[3][1])
                else:
                    tx = pyxel.rndi(8,120)
                    ty = pyxel.rndi(8,120)

        ###### 目標地点（tx,ty）に向けて移動を行う        
        self.mons_walk(i, tx, ty)

    def mons_walk(self, i, tx, ty):
        newdir = 4
        if self.mons_dir[i] != 2:
            nx = int(self.mons[i][0]/8) + self.D[newdir][0]
            ny = int(self.mons[i][1]/8) + self.D[newdir][1]
            tpl = pyxel.tilemaps[0].pget(nx,ny)
            if tx < self.mons[i][0] and tpl != (1,0):
                self.mons_dir[i] = newdir
                self.mons[i][0] += (self.D[self.mons_dir[i]][0] * 1)
                self.mons[i][1] += (self.D[self.mons_dir[i]][1] * 1)
                return

        newdir = 2
        if self.mons_dir[i] != 4:
            nx = int(self.mons[i][0]/8) + self.D[newdir][0]
            ny = int(self.mons[i][1]/8) + self.D[newdir][1]
            tpl = pyxel.tilemaps[0].pget(nx,ny)
            if tx > self.mons[i][0] and tpl != (1,0):
                self.mons_dir[i] = newdir
                self.mons[i][0] += (self.D[self.mons_dir[i]][0] * 1)
                self.mons[i][1] += (self.D[self.mons_dir[i]][1] * 1)
                return

        newdir = 1
        if self.mons_dir[i] != 3:
            nx = int(self.mons[i][0]/8) + self.D[newdir][0]
            ny = int(self.mons[i][1]/8) + self.D[newdir][1]
            tpl = pyxel.tilemaps[0].pget(nx,ny)
            if ty < self.mons[i][1] and tpl != (1,0):
                self.mons_dir[i] = newdir
                self.mons[i][0] += (self.D[self.mons_dir[i]][0] * 1)
                self.mons[i][1] += (self.D[self.mons_dir[i]][1] * 1)
                return

        newdir = 3
        if self.mons_dir[i] != 1:
            nx = int(self.mons[i][0]/8) + self.D[newdir][0]
            ny = int(self.mons[i][1]/8) + self.D[newdir][1]
            tpl = pyxel.tilemaps[0].pget(nx,ny)
            if ty > self.mons[i][1] and tpl != (1,0):
                self.mons_dir[i] = newdir
                self.mons[i][0] += (self.D[self.mons_dir[i]][0] * 1)
                self.mons[i][1] += (self.D[self.mons_dir[i]][1] * 1)
                return

        ### 止まらないよ！
        while True:
            dir = pyxel.rndi(1,4)
            nx = int(self.mons[i][0]/8) + self.D[dir][0]
            ny = int(self.mons[i][1]/8) + self.D[dir][1]
            tpl = pyxel.tilemaps[0].pget(nx,ny)
            if tpl != (1,0):
                self.mons_dir[i] = dir
                self.mons[i][0] += (self.D[self.mons_dir[i]][0] * 1)
                self.mons[i][1] += (self.D[self.mons_dir[i]][1] * 1)
                return

App()

