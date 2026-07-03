### Maybe: [Asymmetric Bounded Nim](nim_variant/asymmetric_bounded_nim.py)
Documentation: [nim_variant/asymmetric.md](nim_variant/asymmetric.md)\
3 heap Nim but you can remove any amount from $x$, up to $x$ from $y$, and up to $y$ from $z$.

### Second best: [Restricted Wythoff](wythoffs_game/restricted_wythoff.py)
Documentation: [wythoffs_game/restricted.md](wythoffs_game/restricted.md)\
3 heap Nim but you can remove the same number of chips from two piles, as long as the number of chips removed from a pile is no greater than the size of the third untouched pile.

## Most Promising: [Bounded Wythoff #3](wythoffs_game/bounded_wythoff.py)
Documentation: [wythoffs_game/bounded.md](wythoffs_game/bounded.md)
Types of games where it's 3D Wythoff (Nim + remove same amount from both piles), but instead of the same amount from both piles:
### 1. $0–x$ variant
Remove $x$ chips from one pile and anywhere from $0$ chips to $x$ chips from the second pile

### 2. $0–2x$ variant
Remove $x$ chips from one pile and anywhere from $1$ chip to $2x$ chips from the second pile

#1 and #2 are solved because the game is symmetrical, and so we can choose any pile to be the "x" pile which we can remove any amount from, and the pile with the restriction is the other pile. However, we can just choose the pile where we want to remove the greater amount of chips from to be "x" and then none of the restrictions apply to the other pile as we know the chips removed there will be less than x. Since there is no lower bound for the amount of chips we can remove, any move where we remove any number of chips from two piles satisfies the rules $0–x$ and $0–2x$. 

This is a type of [Moore's Nim](https://doi.org/10.2307/1967321) called $\text{Nim}_k$, where you can remove any number of chips from $k$ piles out of $n$ total piles. In this case, $k=2$ and $n=3$.

A position is a loser iff the binary representation of heap sizes added together without carrying $\equiv0 \pmod{k+1}$, so similar to nim sum which uses mod 2. 

So for variants 1 and 2, just nim sum but with mod 3. 


### 3. $x–2x$ variant
Remove $x$ chips from one pile and anywhere from $x$ chips to $2x$ chips from the second pile.

This is similar to Fraenkel's [$\text{Wyt}(f)$](https://www.wisdom.weizmann.ac.il/~fraenkel/Papers/Wyt(f)_10.pdf) where you only have 2 piles and you can:
1. Take any amount from one pile
2. Take $k>0$ from one pile and $l>0$ from another, where $0<k\le l<f(k)$.

For this variant, if it were with two piles, then $f(k)=2k+1$.
In https://arxiv.org/pdf/math/9809074 they briefly looked at the $2k+1$ case with two piles. 
