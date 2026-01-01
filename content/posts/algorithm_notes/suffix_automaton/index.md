---
title: 後綴自動機（Suffix Automaton）
summary: TBD
date: 2025-12-28
tags:
  - algorithm
  - string algorithm
  - note
---


## 一些廢話

在上這學期的培訓班的時候，作業的題目出現了一題字串處理的題目，助教跟大家說這種題目用 SAM 可以無腦直接輾過去，但當時我對 SAM 是什麼根本不知道~~我只知道它在我們的 codebook 裡面~~。稍微看完介紹後還是沒有很懂，可能跟我當時還沒修完系上的必修「自動機與形式語言」有點關係~~但可能沒有那麼多~~。我其實從很久以前就對字串的演算法很有障礙，所以我希望可以好好的把觀念釐清，因此特地寫這邊筆記來整理一下~~還有為了培訓班加分~~。

## 簡介

後綴自動機（Suffix Automaton，簡稱 SAM）是一個可以快速查詢單個字串（事實上可以做多個，但這篇文章先不會帶過）的所有子字串的資訊的資料結構。也就是說它是一個將子字串資訊壓縮後高效儲存的資料結構。如果我們把字串可能出現的字母集 $\Sigma$ 的大小當作常數的話，後綴自動機的空間和使用時間都是 $O(n)$ 的。

作為 sneak peek，後綴自動機可以解決的問題包含但不限於：
- 檢查一個字串是否為另一個字串的子字串
- 計算一個字串的不同子字串數量
- 找到最小的環狀旋轉（Smallest Cyclic Shift）


## 前情提要

接下來，我們會先稍微介紹一些等等要看懂會用到的先備知識。

### 什麼是一個自動機？

一個自動機（Automaton）是一個可以接受或拒絕輸入字串的數學模型。簡單想就是一個有向圖，每個節點我們會把它叫做「狀態」（State），然後每條邊會有一個字元 $c$，代表我們在目前的狀態下讀取到字元 $c$ 之後會轉移到哪一個狀態。當我們從起始狀態開始讀取輸入字串的每一個字元，然後根據圖上的邊進行狀態轉移，最後如果我們停在一個接受狀態（Accept State），那麼這個自動機就接受這個輸入字串，否則就拒絕它。所謂的接受與否就是在說這個字串是不是我們要的東西。舉例來說在我們的後綴自動機就是它是不是我們的來源字串的後綴。

### 後綴自動機的定義

一個字串 $s$ 的後綴自動機是一個決定性的有限自動機（Deterministic Finite Automaton, DFA）。Deterministic 是什麼意思呢？在計算理論（自動機課程比較有道理的名稱）中，決定性的意思就是每個可能的字元都有洽好一條邊可以走，這樣可以保證所有的的字串都會對應到這個圖上面的某一條路徑（可能是歸零用的死路）。這樣就能保證我們可以把任何字串都丟進這個圖上，在走路的過程中我們可以在路徑上蒐集資訊來幫助我們解決問題。

有些其他後綴自動機的好性質，比如它是最輕便（最小）的能做到相同事情的自動機。

在後綴自動機中，每一個可能的路徑都會對應到來源字串 $s$ 的一個子字串。也就是說，如果我們從起始狀態出發，然後根據輸入字串 $t$ 上的每一個字元走路，如果我們能夠成功走完整個字串 $t$，那麼這個字串 $t$ 就是來源字串 $s$ 的一個子字串。

## 演算法

我們會先介紹一些相關的字詞，在邊看懂它們的定義的時候我們將會構造出一個能夠在線性時間做出一個字串 $s$ 的後綴自動機的演算法。

### 結尾位置 $\text{endpos}$

對於一個字串 $s$ 的子字串 $t$，我們定義 $\text{endpos}(t)$ 為所有在 $s$ 中出現的 $t$ 的結尾位置所組成的集合。舉例來說，假設 $s = \text{"ababc"}$，那麼 $\text{endpos}(\text{"ab"}) = \{1, 3\}$，因為在 $s$ 中 "ab" 出現在位置 0-1 和 2-3。（0-based）

如果兩個字串 $t_1$ 和 $t_2$ 的所有終點位置都相同，也就是說 $\text{endpos}(t_1) = \text{endpos}(t_2)$，那麼我們就說 $t_1$ 和 $t_2$ 是等價的（equivalent）。例如在上面的例子中，$\text{endpos}(\text{"ab"}) = \text{endpos}(\text{"b"})$，所以 "ab" 和 "b" 是等價的。

在後綴自動機中，每一個狀態都會對應到一個 $\text{endpos}$ 集合。也就是說 SAM 裡面的狀態數量（節點數量）就是不同 $\text{endpos}$ 集合的數量。

為了接下來的演算法，我們會有一些引理：

### 後綴連結邊（Suffix Link）$\text{link}$

對於自動機上某個狀態 $v$，它會對應到一個最長的字串 $w$，所有對應到同樣 $\text{endpos}$ 集合的字串都會是 $w$ 的後綴，我們稱 $w$ 為 $v$ 的代表。不是全部它的後綴都會跟 $w$ 在同一個狀態上，想像 $\text{"ababb"}$ 中的 $\text{"b"}$ 和 $\text{"ab"}$，它們不會對應到同一個狀態，因為 $\text{"b"}$ 出現的次數比較多。

我們希望能夠找到一個狀態 $u$，使得 $u$ 的代表是 $w$ 的後綴中 $\text{endpos}$ 跟 $w$ 不一樣的字串中長度最長的。這樣我們就說 $\text{link}(v) = u$。我們稱這條邊為後綴連結邊（Suffix Link）。把起始狀態想像成空的字串，那麼所有狀態都一定會有一條後綴連接邊。

### 狀態的長度 $\text{len}$

對於自動機上某個狀態 $v$，我們定義 $\text{len}(v)$ 為 $v$ 的代表字串的長度。也就是說，$\text{len}(v)$ 是所有對應到狀態 $v$ 的字串中最長的那一個字串的長度。

而 $v$ 能代表的字串中長度最短的我們叫他 $\text{minlen}(v)$，也就是說 $v$ 存的後綴長度範圍是 $[\text{minlen}(v), \text{len}(v)]$，其中 $\text{minlen}(v) = \text{len}(\text{link}(v)) + 1$ for $v \neq v_0$。

如果我們在某個狀態 $v$ 一直沿著 $\text{link(v)}$ 走下去，我們經過的所有狀態將包括所有 $v$ 的代表字串的後綴所對應到的狀態。

### 建構的演算法

我們會用一個線性時間的演算法來建構後綴自動機。這個演算法是在線性時間內一個字元一個字元地把字串加入到自動機中（也就是說它是在線的）。

可以想像一開始我們有個只有初始狀態 $v_0$ (index 0) 的自動機，它的 $\text{len}(v_0) = 0$、 $\text{link}(v_0) = -1$。然後我們會一個字元一個字元地把字串 $s$ 加入到自動機中。假設我們已經把字串 $s[0 \ldots i-1]$ 加入到自動機中了，現在我們要把字元 $s[i]$ 加入進去。

我們會維護一個變數 $\text{last}$，它代表目前整個自動機中對應到字串 $s[0 \ldots i-1]$ 的狀態。當我們要加入字元 $s[i]$ 時，我們要先建立一個代表這個新的後綴的新狀態 $\text{cur}$，它的 $\text{len}(\text{cur}) = \text{len}(\text{last}) + 1$。然後我們從 $\text{last}$ 開始，沿著自動機的邊往上走，對每一個狀態，如果它有一條標記為 $s[i]$ 的邊，我們就停下來然後把這個狀態先叫做 $p$。如果找不到 $p$ 我們就把 $\text{link}(\text{cur})$ 設為 $v_0$ (0)。

接著如果我們找到了 $p$，我們檢查從 $p$ 出發標記為 $s[i]$ 的邊所到達的狀態 $q$。如果 $\text{len}(p) + 1 = \text{len}(q)$，那麼我們就把 $\text{link}(\text{cur})$ 設為 $q$。

否則，我們需要複製出一個新的狀態 $\text{clone}$，修改 $\text{len}(\text{clone}) = \text{len}(p) + 1$，並且把 $\text{link}(q)$ 和 $\text{link}(\text{cur})$ 都設為 $\text{clone}$。然後我們從 $p$ 開始，沿著 suffix links 的邊往上走，對每一個狀態如果它的邊用 $s[i]$ 走道 $q$，我們就把它改成指向 $\text{clone}$，直到找不到這樣的狀態為止。

最後，我們把 $\text{last}$ 設為 $\text{cur}$，然後繼續處理下一個字元。

之後我們可以把 $\text{last}$ 回溯到每一個後綴來標記哪些狀態是接受狀態。

有關空間複雜度，可以簡單的想像每次我們增加最多兩個狀態（$\text{cur}$ 和可能的 $\text{clone}$），所以整個自動機的狀態數量是 $O(n)$ 的。而邊的修改數量也是線性的，可以從走 suffix link 的過程去想像：每次走的時候都在減少 $\text{len}$ 的值，而 $\text{len}$ 最多從 $n$ 減少到 0，所以整個過程中邊的修改數量也是 $O(n)$ 的。

時間的複雜度也是 $O(n)$ 的，因為每個字元我們最多增加兩個狀態，而每次走 suffix link 的過程中每個狀態最多被訪問一次。

注意這邊我們把 $|\Sigma|$ 當作常數來看待，所以每個狀態的邊數量也是常數。如果要把它當變數的話，那麼空間複雜度會是 $O(n|\Sigma|)$，或可以用平衡樹之類的資料結構來以時間換取空間。

更詳細的證明請參閱參考資料，裡面除了有更完整的證明之外還有最佳性的證明（不能再更少之類的）。


## 實作

最簡單的情況可以用一個 struct 來存一個狀態，或著是說節點：
```cpp
struct State {
    int len, link;
    map<char, int> nxt;
}
```

或

```cpp
struct State {
    int len, link;
    vector<int> nxt; // size = |Σ|
}
```

我們可以用一個 vector 來存整個自動機的所有狀態，所以整個構造函數可以長這樣：

```cpp

void init() {
    state[0].len = 0;
    state[0].link = -1;
    last = 0;
    sz++;
}

void extend(int id) { // id = s[i] - 'a' 之類的
    int cur = sz++;
    state[cur].len = state[last].len + 1;
    int p = last;
    while (p >= 0 && !state[p].nxt[id]) {
        state[p].nxt[id] = cur;
        p = state[p].link;
    }

    if (p == -1) {
        state[cur].link = 0;
    } else {
        int q = state[p].nxt[id];
        if (state[p].len + 1 == state[q].len) {
            state[cur].link = q;
        } else {
            int clone = sz++;
            state[clone].len = state[p].len + 1;
            state[clone].nxt = state[q].nxt;
            state[clone].link = state[q].link;
            while (p >= 0 && state[p].nxt[id] == q) {
                state[p].nxt[id] = clone;
                p = state[p].link;
            }
            state[q].link state[cur].link = clone;
        }
    }

    last = cur;
}

```

（之後再附贈一個更完整的版本）


### 經典功能範例

#### 相異子字串數量

計算一個字串的相異子字串數量可以透過後綴自動機來達成。對於每一個狀態 $v$，它能代表的子字串長度範圍是 $[\text{minlen}(v), \text{len}(v)]$，因此這個狀態能夠貢獻 $\text{len}(v) - \text{minlen}(v) + 1$ 個不同的子字串。

只要把所有狀態的這個值加起來，我們就能得到整個字串的相異子字串數量。

```cpp
ll distinctSubstr() {
    ll ret = 0;
    for (int v = 1; v < sz; v++) {
        ret += state[v].len - state[state[v].link].len;
    }
    return ret;
}
```

#### 相異子字串長度和

跟算上面的類似，加個等差數列的和就好了。

#### 最小環狀旋轉

我們建一個 $s || s$（字串接字串）的後綴自動機，然後從起始狀態開始走 $n$ 步（$n$ 是原本字串的長度），每次都選擇邊上字元最小的那一條邊，最後停下來的時候我們走過的路徑就是最小環狀旋轉。

#### 字串出現次數

對於某個字串 $t$ 在 $s$ 中出現的次數，我們可以定義 $\text{cnt}(v) = |\text{endpos}(v)|$。所有等價的字串出現的次數都一樣，他們的終點們會等於每個 $\text{endpos}$ 裡面的元素。

我們對於所有狀態可以把 $\text{cnt}(v)$ 初始化成 0，每個 $v$ 都會對 $\text{cnt}(\text{link}(v))$ 產生 $\text{cnt}(v)$ 的貢獻。也就是說把所有狀態照 $\text{len}$ 由大到小傳遞就可以有效地算出每個狀態的 $\text{cnt}$。

如果我們要查詢字串 $t$ 在 $s$ 中出現的次數，我們可以從起始狀態開始，然後根據 $t$ 上的每一個字元走路，如果能夠成功走完整個字串 $t$，那麼我們就回傳 $\text{cnt}(v)$，其中 $v$ 是我們最後停下來的狀態；否則回傳 0。

#### 最長共同子字串

## 例題

- [CSES - Counting Patterns](https://cses.fi/problemset/task/2103)
- [CSES - Pattern Positions](https://cses.fi/problemset/task/2104)
- [CSES - Distinct Substrings](https://cses.fi/problemset/task/2105)
- [CF - 235C Cyclical Quest](https://codeforces.com/problemset/problem/235/C)

## 參考資料

- [CP Algorithm - Suffix Automaton](https://cp-algorithms.com/string/suffix-automaton.html)
- [OI Wiki](https://oi-wiki.org/string/sam/)
