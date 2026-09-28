local out='D:/heroschool/sprites/wizard-work/'
local combat=Image{fromFile=out..'combat-source.png'}

local work=Image{fromFile=out..'source.png'}
local combatRows={0,298,568,845,1097,1402}
local workRows={0,265,495,763,1025,1267,1536}
local combatCols={0,290,563,855,1122}
local workCols={0,265,525,780,1024}
local names={'idle','attack','hit','down','win','weed','scrub','dust','carry','meditate','read'}
local ms={180,100,100,180,180,220,200,220,180,400,300}
-- Source-space body axes, independent of ponytail and held prop bounds.
-- All four poses share the same ground line; feet may move around the root.
local bodyPivots={
 [8]={x={134,384.5,639,895},y={1013,1011,1013,1014}},
 [9]={x={137,399,648.5,900.5},y={1248,1248,1249,1249}},
 [10]={x={130.5,385.5,639.5,891},y={1501,1502,1502,1502}}
}
local s=Sprite(256,256,ColorMode.RGB);s.layers[1].name='wizard'
local sheet=Image(1024,2816,ColorMode.RGB)
for row=0,10 do
 local src=row<5 and combat or work
 local ys=row<5 and combatRows or workRows
 local xs=row<5 and combatCols or workCols

 if row==1 then xs={0,300,580,885,1122} end
 if row==3 then xs={0,300,547,831,1122} end
 local rr=row<5 and row or row-5
 local factor=row<5 and 0.40 or 0.42
 for col=0,3 do
  local fi=row*4+col+1;if fi>1 then s:newEmptyFrame() end
  s.frames[fi].duration=ms[row+1]/1000
  local im=Image(xs[col+2]-xs[col+1],ys[rr+2]-ys[rr+1],ColorMode.RGB)
  local frameSource=src
  im:drawImage(frameSource,Point(-xs[col+1],-ys[rr+1]))
  local x0,y0,x1,y1=im.width,im.height,0,0
  for y=0,im.height-1 do for x=0,im.width-1 do
   local p=im:getPixel(x,y)
   if app.pixelColor.rgbaA(p)>127 then
    im:drawPixel(x,y,app.pixelColor.rgba(app.pixelColor.rgbaR(p),app.pixelColor.rgbaG(p),app.pixelColor.rgbaB(p),255))
    x0=math.min(x0,x);y0=math.min(y0,y);x1=math.max(x1,x);y1=math.max(y1,y)
   else im:drawPixel(x,y,0) end
  end end
  assert(x1>x0 and y1>y0,'Empty frame')
  im:resize(math.floor(im.width*factor),math.floor(im.height*factor))
  local dest=Image(256,256,ColorMode.RGB)
  local dx=math.floor(128-(x0+x1)*factor/2)
  local dy=math.floor(170-y1*factor)
  local pivot=bodyPivots[row]
  if pivot then
   local scaleX=im.width/(xs[col+2]-xs[col+1])
   local scaleY=im.height/(ys[rr+2]-ys[rr+1])
   dx=math.floor(128-(pivot.x[col+1]-xs[col+1])*scaleX+0.5)
   local py=type(pivot.y)=="table" and pivot.y[col+1] or pivot.y
   dy=math.floor(170-(py-ys[rr+1])*scaleY+0.5)
  end
  dest:drawImage(im,Point(dx,dy))
  s:newCel(s.layers[1],fi,dest,Point(0,0))
  sheet:drawImage(dest,Point(col*256,row*256))
 end
 local tag=s:newTag(row*4+1,row*4+4);tag.name=names[row+1]
end
s:saveAs(out..'wizard-complete.aseprite')
sheet:saveAs(out..'wizard-complete.png')
