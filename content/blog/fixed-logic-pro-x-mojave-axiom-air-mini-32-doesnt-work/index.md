---
title: 'FIXED: Logic Pro X + Mojave + Axiom Air mini 32 doesn’t work'
date: '2019-10-05'
comments: true
draft: false
categories:
- musica-video
- technology-ict
tags:
- axiom-air-mini-32
- dav
- logic-pro-x
- music
- problem
- solution
- usbhub
original_url: https://www.danielebailo.it/2019/10/05/fixed-logic-pro-x-mojave-axiom-air-mini-32-doesnt-work/
migration_source: wordpress-personale
cover: /uploads/2019/10/IMG_20191005_131730-2192236633-1570276742265-1.jpg
summary: 'If you got here, you are probably one of those who just purchased an Axiom
  Air Mini 32 midi keyboard controller, plugged it in, and tried to have some fun
  with Logic Pro X.
  And it doesn’t work!

  No worries.
  I have a solution.'
---

If you got here, you are probably one of those who just purchased an Axiom Air Mini 32 midi keyboard controller, plugged it in, and tried to have some fun with Logic Pro X.

**And… surprise… IT DOESN’T WORK!**

No worries.

I’ve a solution.

And I’ll give it to you.

**If you want to read it right now, just scroll down.**

First, let’s try to understand the causes. I went through many posts reporting the same problem.

It seems that with latest Macosx update to Mojave, something has changed with the way USB 3 is managed.

In case you want additional details… go to these posts.

<https://getsatisfaction.com/m-audio/topics/axiom-air-mini-32-logic-pro-x-help>

<https://getsatisfaction.com/m-audio/topics/using-axiom-air-32-mini-with-logic-pro-x>

<https://getsatisfaction.com/m-audio/topics/setup-axiom-air-mini-32-with-logic-pro-9>

<https://getsatisfaction.com/m-audio/topics/axiom-air-32-mini-doesnt-work-with-logic-pro-x>

### Potential solutions (didn’t work for me)

Many posts suggest to solve the issue with software fixes.

First by downloading e installing [Hypercontrol drivers](http://m-audio.com/support/download/software/axiom-air-mini-32-hyper-control-logic-v1.0.2)

. (also here <https://m-audio.com/kb/article/1684>)

Secondly by checking the controller is actually sending data, for sintance by using **Audio Midi Setup**  (by default on Macosx, just start typing “midi”) on Spotlight.

Thirdly, by working with the [control surfaces](https://www.noterepeat.com/products/m-audio/keyboard-controllers/axiom-air-series/269-m-audio-axiom-air-series-setup-with-logic-pro-x) in Logic...

But these didn’t work (for me), because it’s an hardware problem.

## Final working Fix

The solution is simple, and was proposed in a post I can't find now (if you have the original post, send me a message and I'll be happy to give credits):

**Do not connect Midi Keyboard straight to the USB port, but go through a USB hub, possibly a USB2 hub.**

The picture below shows the working setup

![](/uploads/2019/10/Senza-nome_3-1.jpg)

As simple as this. A nice workaround… that makes eventually the whole thing work!

If you liked this post, please comment and share.
