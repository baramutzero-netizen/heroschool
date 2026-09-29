local out='D:/heroschool/sprites/timemage-work/'
local combat=Image{fromFile=out..'combat-source.png'}
local work=Image{fromFile=out..'source.png'}
local combatRows={0,287,566,844,1104,1402}
local workRows={0,274,508,771,1033,1260,1536}
local names={'idle','attack','hit','down','win','weed','scrub','dust','carry','meditate','read'}
local ms={180,100,100,180,180,220,200,220,180,400,300}
-- Root tracks the body, not the hair/cape/tray bounding box.
local roots={
 [0]={x={147,425,704,986},y={261,261,263,261}},
 [1]={x={137,414,677,986},y={534,534,535,534}},
 [4]={x={148,438,720,986},y={1363,1367,1367,1363}},
 [8]={x={134,395,650,910},y={1011,1012,1011,1011}},
 [9]={x={142,399,657,914},y={1244,1243,1244,1244}},
 [10]={x={139,397,654,912},y={1497,1497,1497,1497}}
}
local s=Sprite(256,256,ColorMode.RGB);s.layers[1].name='timemage'
local sheet=Image(1024,2816,ColorMode.RGB)
for row=0,10 do
 local src=row<5 and combat or work
 local ys=row<5 and combatRows or workRows
 local xs=row<5 and {0,280,560,840,1122} or {0,256,512,768,1024}
 if row==1 then xs={0,280,570,858,1122} end
 if row==7 then xs={0,260,532,770,1024} end
 local rr=row<5 and row or row-5
 local factor=0.5
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
s:saveAs(out..'timemage-complete.aseprite')
sheet:saveAs(out..'timemage-complete.png')
