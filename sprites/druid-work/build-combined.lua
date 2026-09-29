local out='D:/heroschool/sprites/druid-work/'
local combat=Image{fromFile=out..'combat-source.png'}
local work=Image{fromFile=out..'source.png'}
local combatRows={0,298,575,846,1088,1402}
local workRows={0,280,511,777,1038,1264,1536}
local names={'idle','attack','hit','down','win','weed','scrub','dust','carry','meditate','read'}
local ms={180,100,100,180,180,220,200,220,180,400,300}
-- Root tracks the body, not the hair/cape/tray bounding box.
local roots={
 [0]={x={134,413,684,962},y={280,279,278,280}},
 [1]={x={134,428,683,964},y={552,552,550,553}},
 [4]={x={148,427,690,978},y={1359,1359,1359,1359}},
 [8]={x={128,385,641,895},y={1016,1016,1015,1017}},
 [9]={x={138,396,650,906},y={1249,1249,1249,1249}},
 [10]={x={128,381,638,895},y={1506,1506,1506,1506}}
}
local s=Sprite(256,256,ColorMode.RGB);s.layers[1].name='druid'
local sheet=Image(1024,2816,ColorMode.RGB)
for row=0,10 do
 local src=row<5 and combat or work
 local ys=row<5 and combatRows or workRows
 local xs=row<5 and {0,280,560,840,1122} or {0,256,512,768,1024}
 if row==7 then xs={0,256,525,768,1024} end
 local rr=row<5 and row or row-5
 local factor=row<5 and 0.46 or 0.5
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
s:saveAs(out..'druid-complete.aseprite')
sheet:saveAs(out..'druid-complete.png')
