---
title: 模擬退火（Simulated Annealing）
summary: 一個物理啟發的啟發式演算法
date: 2024-12-25
math: true
tags:
  - algorithm
  - stochastic algorithm
  - note
---

## 前言

前陣子，有位資工系大二的學長跟我說，對資工系的學生來說物理沒有什麼用，不用太認真念沒有關係。但其實有很多物理現象所啟發的演算法，我在讀到的時候覺得挺有趣的，而我修的課裡剛好有讓我寫一下相關的介紹契機，所以就來寫一下了。

## 啟發我的題目

今年，我在臺大的 ICPC 培訓班練習時遇到了一個問題：

給定你三維空間中的 $N$ 個點，尋找最小的球，使得所有的點都在這個球裡面。

測試範圍 $ 3 \le N \le 100 $, $ -10^5 \le x_n, y_n, z_n \le 10^5 $。

簡單的說，這就是一個最小包覆圓問題。基本上可以用以下的想法去做：
- 隨機打亂點的順序，降低期望時間複雜度。
- 依序加入點，如果這個點不在包覆圓裡面，就更新包覆圓。
    - 新加入的點得在這些點的最小包覆圓上，所以可以找他和前面的人的外心，然後更新包覆圓。

這個做法叫做 Welzl's algorithm，期望上的時間複雜度是 $\mathcal O(N)$，但我們的模板裡面沒有整理好的三維外心公式，所以有點小麻煩。

因為我們隊伍之前遇到過二維的最小包覆圓問題，所以我們比賽的時候深信不疑，只往這個方向去想，所以覺得整理外心公式然後再把模板的所有東西都改成三維有點麻煩，就先跑去做別題了。

但在補題的時候，我們發現了其他人的解法裡面有一堆程式碼長度遠低於預期的，於是我們就去看了一下，發現他們用了一個叫做模擬退火的演算法。於是我就決定來研究一下這個演算法。

## 簡介

模擬退火（simulated annealing）是一種元啟發式（metaheuristic）演算法。什麼是元啟發式呢？啟發式演算法通常是藉由一些真實世界的現象或是一些經驗法則來設計的演算法，可以利用這些特定的啟發來解決問題（通常會是近似的解，不一定會是最好的，可以想想併查集的啟發式合併）。而元啟發式演算法則是一種框架，「元」這個字代表它能夠拿來解決不只一種問題。

回歸正題，模擬退火是一種基於物理現象的演算法。這個演算法的名字來自於冶金學中的退火過程，這個過程是將金屬加熱到高溫，然後慢慢冷卻，使得金屬的晶格排列更加有序，從而提高金屬的強度。為什麼要先加熱再冷卻呢？高中物理時我們學過（沒學過也沒差，不會真的講很難），溫度是粒子動能的宏觀性質。也就是說，把溫度提升之後，粒子的運動會變得更加激烈，這樣就有機會讓粒子能跳出自己原本在晶格裡的位置，落到一個位能更低的位置（想像一個位能很高的晶格排列代表代表他很不穩定，外界一刺激他就有機會釋放位能）。在金屬冷卻的過程，粒子跳出原本位置的能力會越來越低，最終找到一個穩定的位置。如此一來，透過一次加熱和穩定的冷卻，我們就可以得到一個比較好的晶格排列。

而模擬退火的演算法也是如此。我們可以把這個演算法想像成一個在解空間裡面遊走的粒子，透過不斷降低溫度，改變他能跳躍的範圍，最終找到一組很接近最佳解（有可能就是最佳解本人）的解。

## 一些和物理的連結

### 能量函數

首先，我們要定義一個我們 **想要最小化** 的能量函數 $E$，這個函數會根據解的好壞來給予一個數值，通常會是跟題目答案很像的型式。以最小包覆球為例，我們的 $E$ 就是包覆球的半徑，我們希望這個半徑越小越好。

### 選擇下一組解

我們的粒子（解）在空間（解空間）裡面遊走，這個空間可能是有限的，也可以是無限的。每個可能的解都是一個狀態（state），在統計力學裡面，可以把它想像成一個粒子所有可測量的物理變量。

那我們要怎麼決定我們的粒子（解）的下一個嘗試移動到的狀態呢？我們的粒子只能變成他的鄰居（和他相似的狀態）。而這個鄰居的定義也可能隨著溫度的降低而改變。可以直觀的想像成，當溫度很高時，我們的粒子可以跳到很遠的地方，但當溫度很低時，我們的粒子只能在原地晃來晃去，但不一定每個題目都需要有隨溫度變化的鄰居定義，**但當前狀態不能和下一個狀態相差太遠是一個很重要的條件**。

### 選擇解的機制

波茲曼分佈（Boltzmann distribution）是一個描述粒子在不同能量狀態下的機率分佈。可以寫成：

\[ p_s \propto \exp\Big(-\frac{E_s}{k_b T}\Big) \]

其中
- $s$ 是粒子的狀態（在模擬退火裡面，就是我們的一組解）
- $p_s$ 是粒子在 $s$ 狀態的機率
- $E_s$ 是粒子在 $s$ 狀態的能量
- $k_b$ 是波茲曼常數
- $T$ 是溫度

這個公式的意義是，粒子在能量較低的狀態的機率會比較高，而在能量較高的狀態的機率會比較低。好奇的你可能會問，為什麼是正比呢？因為所有狀態的機率總和要等於 1，所以在不同溫度下，加起來的總合會不一樣。至於為什麼要長這個樣子，因為系統傾向於處於熵最大的狀態，因此會符合這個分布，詳細的內容可以去參考統計力學的教科書之類的。

而將兩個狀態的機率相除，可以得到波茲曼因子（Boltzmann factor）：

\[ \frac{p_t}{p_s} = \exp\Big(-\frac{E_t - E_s}{k_b T}\Big) = \exp\Big(-\frac{\Delta E}{k_b T}\Big) = P(\Delta E)\]

如此一來，我們就有了一個在不同溫度下，不同狀態間的機率比較函數，可以發現當 $\Delta E$ 越小或是 $T$ 越大時，這個比較函數會越大，也就是說，當溫度越高時，我們會更容易接受一個比較差的解，這和物理上的現象是一致的。

而在演算法中，我們決定要不要接受一個新的解，可以透過以下的方式來決定：

- 如果 $\Delta E \le 0$，我們就接受這個新的解
- 如果 $\Delta E > 0$，我們就以 $P(\Delta E)$ 的機率接受這個新的解

**這個機制就是模擬退火的核心。**

至於 $k_b$ 呢？在物理上，$k_b$ 是波茲曼常數，其值約為 $1.38 \times 10^{-23} \, \text{J/K}$。但在演算法中，我們可以發現 $k_b$ 的作用其實就是縮放溫度的大小，跟把初始溫度改變是一樣的意思。

但注意到，我們可能**需要適度的縮放 $P(\Delta E)$**，否則演算法會隨機出一個很差的解也還是更新，詳見下面的範例。

最後，以 $P(\Delta E)$ 的機率採樣可以以 [Metropolis-Hastings algorithm](https://en.wikipedia.org/wiki/Metropolis%E2%80%93Hastings_algorithm) 來實作。

```cpp
random_device rd;
mt19937 rng(rd());

uniform_real_distribution<db> threshold(0, 1);

double magic = ???; // problem dependent

auto accept = [&](db dE, db T) {
    return dE <= 0 || exp(-dE / T) / magic > threshold(rng);
};
```

### 降溫機制

接下來，我們要來討論如何降溫，在現實生活中，我們有牛頓冷卻定律，可以用來描述物體的溫度變化速率：

\[ \frac{dT}{dt} = -k(T - T_f) \]

其中
- $T$ 是冷卻（或升溫）的溫度
- $T_f$ 是環境的溫度（常數）
- $k$ 是冷卻常數

稍微整理一下：

\[ \frac{dT}{T - T_f} = -k dt \]

\[\int \frac{dT}{T - T_f} = -k \int dt \]

\[ \ln(T - T_f) = -kt + C \]

代入邊界條件 $T(\infty) = T_f$：

\[ T = T_f + (T_0 - T_f) \exp(-kt) \]

我們可以看到每當 $\Delta t$ 過去，$(T_0 - T_f)$ 就會乘上一個小於 $1$ 的常數。

一般來說，我們會把 $T_f$ 設為 $0$，$T_0$ 設成一個大數，然後在 $T$ 小於一個值時停止冷卻，這樣就可以模擬出一個冷卻的過程。

除了這種降溫程序（Schedule）之外，也有其他的降溫程序，這邊列出幾種更新方法：

- 指數降溫：$T' = T \cdot r$（就是上面的的作法）
- 線性降溫：$T' = T - r$
- 邏輯降溫：$T' = \displaystyle \frac{T}{1 + r T}$ 

這些降溫程序的選擇會影響到模擬退火的效果，不過**一般來說，指數降溫是最常見的**。
一些實作也會將程序混合或是採用不同的 $r$ 值，以達到更好的效果。

## 演算法流程

總結一下，模擬退火的演算法流程如下：

1. 初始化溫度 $T$ 和初始解 $s$
2. 重複以下步驟直到溫度降到一個很小的值：
    1. 隨機選擇一個鄰居 $s'$
    2. 計算 $\Delta E = E(s') - E(s)$
    3. 如果 $\Delta E \le 0$，更新 $s \leftarrow s'$
    4. 如果 $\Delta E > 0$，以 $P(\Delta E)$ 的機率更新 $s \leftarrow s'$
    5. 降溫 $T \leftarrow T'$

## 範例

### 經典範例

我們以 [P1337 [JSOI2004] 平衡點](https://www.luogu.com.cn/problem/P1337) 作為一個經典的舉例。

題目敘述：給定你一些桌子上的洞 $(x_i, y_i)$，每個洞會用繩子掛上一個重量為 $w_i$ 的重物，問你將這些繩子的一端綁在一起後，最後連接點會在哪裡（就是如果繩子綁在那裡，那裡所受拉力的合力為 $0$）。

這個問題需要先用到一點基本的物理觀念：重力位能

如果系統要平衡，那麼系統的重力位能總和要最小，因為系統會往重力位能最低的地方移動。可以想像如果你把連接點往某個重物的洞口移動 $\Delta r$ 的距離，那麼這個重物的重力位能改變量 $\Delta U$ 會是：

\[ \Delta U = -w_i \cdot \Delta r \]

我們可以將每個點的重力位能零位點設成連接點 $(x, y)$ 在 $(x_i, y_i)$ 時，如此一來，每個點的重力位能就會是：

\[ U_i = w_i \cdot \sqrt{(x_i - x)^2 + (y_i - y)^2} \]

如此一來，我們就可以得到一個能量函數：

\[ E(x, y) = \sum_{i=1}^{n} w_i \cdot \sqrt{(x_i - x)^2 + (y_i - y)^2} \]

而問題就變成了找到一個 $(x, y)$ 使得 $E(x, y)$ 最小。

這個問題的其中一種解法就是模擬退火，我們可以這樣實作：

```cpp
#include <bits/stdc++.h>

using namespace std;

typedef double db;
typedef tuple<db, db, int> Weight;

// calculate the potential energy
db calc(db x, db y, vector<Weight>& weight) {
    db E = 0;
    for (auto& [wx, wy, w]: weight) {
        E += w * sqrt((x - wx) * (x - wx) + (y - wy) * (y - wy));
    }
    return E;
}

// simulated annealing, we will use this function many times
pair<db, db> anneal(const vector<Weight>& weight, db magic) {
    random_device rd;
    mt19937 rng(rd());

    uniform_real_distribution<db> threshold(0, 1), delta(-1, 1);

    db x = 0, y = 0, E = calc(x, y, weight);
    for (db T = 1e4, T_f = 1e-6, r = 0.996; T > T_f; T *= r) {
        db nx = x + delta(rng) * T, ny = y + delta(rng) * T;
        db dE = calc(nx, ny, weight) - E;

        if (dE < 0 || exp(-dE / T) / magic > threshold(rng)) {
            x = nx, y = ny, E += dE;
        }
    }

    return {x, y};
}

int main() {
    int N;
    cin >> N;

    vector<Weight> weight(N);

    for (auto& [x, y, w]: weight) cin >> x >> y >> w;
    
    random_device rd; 
    mt19937 rng(rd());

    uniform_int_distribution<int> randint(100, 1000);

    db x = 325, y = 225;
    for (int i = 0; i < 10; i++) {
        auto [nx, ny] = anneal(weight, randint(rng)); 
        if (calc(nx, ny, weight) < calc(x, y, weight)) x = nx, y = ny;
    } 

    cout << fixed << setprecision(3) << x << ' ' << y << '\n';
}
```

你可能會注意到我們在 $\text{anneal}$ 函數裡面多了一個 $\text{magic}$ 參數，這個參數是用來調整我們的接受機制的，這個參數可以篩除 $(\because \text{magic} > 1)$ 比較差的解，也就是說，我們對於解的要求比較嚴格，這樣可以讓我們的粒子更好的探索解空間。

順帶一提，

\[\sum_{i=1}^{n} ||\mathbf r_i - \mathbf r|| \]

的解 $\mathbf r$ 在數學上又叫做[費馬點](https://en.wikipedia.org/wiki/Fermat_point)。

而這題的答案則是一個帶權重的費馬點。


### 運用在陣列

除了使用在幾何相關的最佳化題目，有些最佳化陣列（排列組合）的問題也可以用模擬退火來解決。

例如 [P4212 外太空旅行](https://www.luogu.com.cn/problem/P4212) 就是一題很適合用模擬退火的題目。

題目敘述希望我們找到一個圖裡的最大團（最大完全子圖），是個 NP-hard 問題，可以很簡單的以模擬退火來解決。

注意到這裡我們要最大化團的大小 $E$，所以找 $\Delta E$ 的時候要反過來算（加負號）。

我的解法定義一個解是一個排列，其能量是最大團的大小，算法是找出最長的前綴使得這個前綴是一個團，然後隨機交換兩個元素，如果新的解比較好就接受，否則以 $P(\Delta E)$ 的機率接受。

```cpp
#include <bits/stdc++.h>

using namespace std;

typedef double db;

int calc(vector<int>& solution, vector< vector<int> >& graph) {
    for (int i = 1; i < solution.size(); i++) {
        for (int j = 0; j < i; j++) {
            if (!graph[solution[i]][solution[j]]) return i; 
        }
    }

    return solution.size();
}

void anneal(vector<int>& solution, vector< vector<int> >& graph) {
    random_device rd;
    mt19937 rng(rd());

    vector<int> tmp = solution;
    shuffle(tmp.begin(), tmp.end(), rng);

    uniform_int_distribution<int> randint(0, tmp.size() - 1);
    uniform_real_distribution<db> rand(0, 1);

    int cur = calc(tmp, graph);
    
    for (db T = 1e3; T > 1e-10; T *= 0.99) {
        int a = randint(rng), b = randint(rng);

        swap(tmp[a], tmp[b]);
        int nxt = calc(tmp, graph);

        if (nxt > cur) {
            cur = nxt;
        } else {
            if (exp((nxt - cur) / T) > rand(rng)) {
                cur = nxt;
            } else {
                swap(tmp[a], tmp[b]);
            }
        }
    }

    if (cur > calc(solution, graph)) solution = tmp;
}

int main() {
    int N;
    cin >> N;

    vector< vector<int> > graph(N, vector<int>(N));

    for (int u, v; cin >> u >> v; ) {
        --u, --v;
        graph[u][v] = 1;
        graph[v][u] = 1;
    }

    vector<int> solution(N);
    iota(solution.begin(), solution.end(), 0);

    random_device rd;
    mt19937 rng(rd());

    for (int i = 0; i < 25; i++) {
        anneal(solution, graph); 
    }

    cout << calc(solution, graph) << '\n';
}
```

在這個題目，我們不需用 $\text{magic}$ 參數，因為鄰居的定義都是固定的（交換兩個元素），所以我們只需要調整溫度的大小就可以了。

## 什麼時候使用模擬退火

> ~~所有的最佳化問題都可以用模擬退火解決~~

對於在空間中找解的題目，尤其是計算幾何的問題，模擬退火是一個很好的選擇，但可能需要 fine-tune 退火的常數並多做幾次。

除此之外，對於其他要找出最佳值的題目，如果能很快地算出你的解的價值，又沒有什麼正規解的想法，你就可以試試看模擬退火。不過，在那之前，請想想有沒有更簡單的解決方法。本質上模擬退火就是在很多山中找出一座山峰，但如果你確定只有一座山峰或只有幾座山峰，你應該考慮三分搜或是爬山演算法（這也是一個類似的隨機演算法，大致上就是直接往比較好的方向走，沒有 random 決定要不要往更差的地方走）之類的。

切記，不要吃毒。

## 例題

- [P2538 [SCOI2008] 城堡](https://www.luogu.com.cn/problem/P2538)
- [P5544 [JSOI2016] 炸彈攻擊1](https://www.luogu.com.cn/problem/P5544)
- [P2503 [HAOI2006] 均分資料](https://www.luogu.com.cn/problem/P2503)
- [P3936 Coloring](https://www.luogu.com.cn/problem/P3936)
- [USACO 2017 Jan Platinum P3. Subsequence Reversal](https://usaco.org/index.php?page=viewproblem2&cpid=698)
- [CF 1556H - DIY Tree](https://codeforces.com/contest/1556/problem/H)
- [CF 1105E - Helping Hiasat](https://codeforces.com/contest/1105/problem/E)
- [AHC 001A - AtCoder Contest Scheduling](https://atcoder.jp/contests/intro-heuristics/tasks/intro_heuristics_a)
- [AGC 035D - Add and Remove](https://atcoder.jp/contests/agc035/tasks/agc035_d)

以下是某些 ICPC 練習賽的題目，防雷一下：
<details>
<summary>展開</summary>

<a href="https://codeforces.com/gym/102006">2018 Syrian Colllegiate Programming Contest pI - Rise of the Robots</a>
<a href="https://codeforces.com/gym/101981">2018-2019 ICPC Nanjing Regional pD - Country Meow</a>

</details>

## 一些小技巧

- 多走幾步：這跟把鄰居的定義改變一樣，可以讓粒子探索更多可能。
- 時間剪枝：一直跑直到快超時了再停止，最後輸出當前最好的解。

可以利用 $\text{clock()}$ 函數來計算時間。

```cpp
#include <ctime>

while (clock() / CLOCKS_PER_SEC < TIME_LIMIT) {
    anneal();
}
```

- 多試試不同的開始點，避免過多局部峰值導致演算法卡住。



## 參考資料

- [Simulated Annealing - Wikipedia](https://en.wikipedia.org/wiki/Simulated_annealing)
- [Boltzmann distribution - Wikipedia](https://en.wikipedia.org/wiki/Boltzmann_distribution)
- [[Tutorial] - Simulated Annealing in Competitive Programming](https://codeforces.com/blog/entry/94437)
- [模擬退火（附加隨機貪心）](https://www.cnblogs.com/ydtz/p/16591381.html)
- [模擬退火 - OI Wiki](https://oi-wiki.org/misc/simulated-annealing/)
