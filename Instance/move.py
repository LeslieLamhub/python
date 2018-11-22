#!/usr/bin/env python
# encoding: utf-8

def move(n,a,b,c):
   if n == 1:
      print("move",a,"-->",c)
   else:
      move(n-1,a,c,b) 
      move(1,a,b,c)
      move(n-1,b,a,c)
move(3,"A","B","C")

  #因为n=3，所以需要将a柱3个盘子（3个盘子暂表示为A1,A2,A3）通过b柱移动到c柱上。

  #move(n-1,a,c,b)  #是为了将a柱中A1，A2，A3由c柱当介质放到b柱中（A1→C，A2→B，C(A1)→B）=（A→C,A→B,C→B)。

  #因为#move(1,a,b,c)固定了A3进入c柱中，所以a柱中的A3不需要移动到b柱中。

  #move(1,a,b,c)    #是为了把a柱中最后一个也就是A3放入c柱中。
  #（A3→C）=(A→C)

  #move(n-1,b,a,c)  #是为了将已经从a柱中移动到b柱中的A1,A2由a柱当介质再放到c柱中
  #（B（A1）→A,B（A2）→C,A(A1)→C）=（B→A,B→C,A→C）
  #
  #A1→C              A→C
  #A2→B              A→B
  #C(A1)→B           C→B
  #A3→C              A→C
  #B（A1）→A         B→A
  #B（A2）→C         B→C
  #A(A1)→C           A→C