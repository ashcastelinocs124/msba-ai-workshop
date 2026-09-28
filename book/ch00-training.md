# 0B How a Model Is Trained

```{raw} html
<p class="wk-lede">A transformer starts out knowing nothing. It learns by one small loop, repeated billions of times: guess the next token, measure the miss, and adjust every weight a little. This page opens up that loop and the optimizer that decides each adjustment; page 0C shows the three stages of training built from it. This page is pre-reading, with no session of its own.</p>
```

```{admonition} Learning objectives
:class: note
- Describe one training step: predict, measure the error, go back through the layers, and let the optimizer adjust the weights.
- Explain gradient descent, the learning rate and momentum.
- Say what the Adam optimizer adds, and why training needs more memory than running a model.
```

## 0B.1 One training step

Every stage of training repeats the same small loop, billions of times. The model reads some text and **predicts** the next token. Its guess is **compared** with the token that really came next, which gives a number for how wrong it was, the **error** (also called the loss). Then the model **goes back** through its layers to work out how much each weight contributed to that error; this step is called **backpropagation**. Finally the **optimizer** turns every weight a little in the direction that would have made the error smaller. Then the next piece of text.

Run the loop yourself. Each step makes "grew" a little more likely after "Deere's revenue", and the error curve falls. Then try a larger learning rate, the size of each turn:

```{raw} html
:file: widgets/ch00-optimizer.html
```

Nothing in the loop checks whether a sentence is true. The model is nudged towards whatever text it is shown, which is why what it reads in each stage of training (page 0C) matters so much.

## 0B.2 Gradient descent

The "go back" step in 0B.1 produces a **gradient**: for every weight, how much the error would change if that weight were nudged up a little. Taken together, the gradient points uphill, the direction in which the error grows fastest. **Backpropagation** is the method that works it out for billions of weights at once.

**Gradient descent** takes a small step the other way, downhill:

> new weight = old weight − learning rate × gradient

Picture walking down a hillside in thick fog: you cannot see the valley, only the slope under your feet, so you take a step downhill and feel again. The **learning rate** is the length of the step. Real training computes each gradient on a small batch of text rather than all of it, so every step is a slightly noisy guess at the true slope; this is called *stochastic* gradient descent.

The landscape is rarely a neat bowl. Along some weights it is steep, along others almost flat, which makes long narrow valleys where plain steps bounce from wall to wall and crawl along the floor. A step too large and the bounces grow until the weights fly off. One old fix is **momentum**: keep part of the previous step's direction, like a ball rolling downhill, so the bounces across the valley cancel out and the pushes along it add up.

The map is the error for two weights; the green dot is the lowest point. Run plain gradient descent, then with momentum, then try each step size:

```{raw} html
:file: widgets/ch00-gd.html
```

## 0B.3 The Adam optimizer

Gradient descent uses one step size for every weight. That is the root of the valley problem: a step small enough for the steep direction is far too small for the gentle one. **Adam** (short for *adaptive moment estimation*, published in 2014) gives every weight its own step size. For each weight it keeps two running averages:

- **the average slope** recently, which is momentum: it smooths out the noise and keeps the steps pointing the same way;
- **the average size of the slope**, whether it has been steep or gentle, jumpy or steady.

Each step moves a weight by its average slope divided by its typical size. A weight whose slope has been steep and jumpy gets small, careful steps; a weight on a gentle, steady slope gets large ones. Race Adam against gradient descent from the same start, and watch the step Adam gives each weight:

```{raw} html
:file: widgets/ch00-adam.html
```

Adam takes steps several times bigger than gradient descent along the gentle weight and several times smaller across the steep one, so it stops bouncing and reaches the bottom in about a quarter of the steps. Adam, and a variant called **AdamW** that also pulls weights gently towards zero, is the usual choice for training large language models, largely because it works across a wide range of learning rates.

It has a cost that shows up on page 0E. Those two running averages are two extra numbers for every weight, kept for the whole of training, so training needs far more memory than answering. A rough rule is about 16 bytes per parameter during training, against 2 to run the model: an 8-billion-parameter model that runs in about 16 GB needs well over 100 GB to train.

## Further reading

- 3Blue1Brown, [*Gradient descent, how neural networks learn*](https://www.youtube.com/watch?v=IHZwWFHWa-w) (video) — the downhill walk, drawn step by step.
- Diederik Kingma and Jimmy Ba, [*Adam: A Method for Stochastic Optimization*](https://arxiv.org/abs/1412.6980) (2014) — the paper that introduced Adam. Technical; the abstract is enough.
