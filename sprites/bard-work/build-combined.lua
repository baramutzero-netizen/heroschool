local out='D:/heroschool/sprites/bard-work/'
local combat=Image{fromFile=out..'combat-source.png'}
local work=Image{fromFile=out..'source.png'}
local combatRows={0,300,570,840,1100,1402}
local workRows={0,250,480,740,990,1232,1536}
local names={'idle','attack','hit','down','win','weed','scrub','dust','carry','meditate','read'}
local ms={180,100,100,180,180,220,200,220,180,400,300}
-- Root tracks the body, not the feather/cape/tray bounding box.
local roots={
 [0]={x={167,434,699,981},y={284,285,284,284}},
 [1]={x={167,440,696,981},y={554,554,554,553}},
 [2]={x={159,436,696,981},y={826,826,826,828}},
 [4]={x={167,433,702,981},y={1361,1361,1361,1361}},
 [8]={x={133,392,647,904},y={975,975,975,975}},
 [9]={x={134,389,643,902},y={1213,1213,1213,1213}},
 [10]={x={133,389,645,902},y={1483,1483,1483,1483}}
}
local s=Sprite(256,256,ColorMode.RGB);s.layers[1].name='bard'
local sheet=Image(1024,2816,ColorMode.RGB)
for row=0,10 do
 local src=row<5 and combat or work
 local ys=row<5 and combatRows or workRows
 local xs=row<5 and {0,280,560,840,1122} or {0,256,512,768,1024}
 if row==7 then xs={0,260,535,780,1024} end
 local rr=row<5 and row or row-5
 local factor=row<5 and 0.49 or 0.52
 for col=0,3 do
  local fi=row*4+col+1;if fi>1 then s:newEmptyFrame() end
  s.frames[fi].duration=ms[row+1]/1000
  local cw,ch=xs[col+2]-xs[col+1],ys[rr+2]-ys[rr+1]
  local im=Image(cw,ch,ColorMode.RGB)
  im:drawImage(src,Point(-xs[col+1],-ys[rr+1]))
  local x0,y0,x1,y1=cw,ch,0,0
  for y=0,ch-1 do for x=0,cw-1 do
   local p=im:getPixel(x,y)
   if app.pixelColor.rgbaA(p)>127 then
    im:drawPixel(x,y,app.pixelColor.rgba(app.pixelColor.rgbaR(p),app.pixelColor.rgbaG(p),app.pixelColor.rgbaB(p),255))
    x0=math.min(x0,x);y0=math.min(y0,y);x1=math.max(x1,x);y1=math.max(y1,y)
   else im:drawPixel(x,y,0) end
  end end
  assert(x1>x0 and y1>y0,'Empty frame')
  im:resize(math.floor(cw*factor),math.floor(ch*factor))
  local sx,sy=im.width/cw,im.height/ch
  local dx=math.floor(128-(x0+x1)*sx/2+0.5)
  local dy=math.floor(170-y1*sy+0.5)
  if roots[row] then
   dx=math.floor(128-(roots[row].x[col+1]-xs[col+1])*sx+0.5)
   dy=math.floor(170-(roots[row].y[col+1]-ys[rr+1])*sy+0.5)
  end
  local dest=Image(256,256,ColorMode.RGB)
  dest:drawImage(im,Point(dx,dy))
  s:newCel(s.layers[1],fi,dest,Point(0,0))
  sheet:drawImage(dest,Point(col*256,row*256))
 end
 local tag=s:newTag(row*4+1,row*4+4);tag.name=names[row+1]
end
s:saveAs(out..'bard-complete.aseprite')
sheet:saveAs(out..'bard-complete.png')
