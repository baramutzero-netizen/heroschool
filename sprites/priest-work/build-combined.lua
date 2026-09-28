local out='D:/heroschool/sprites/priest-work/'
local combat=Image{fromFile=out..'combat-source.png'}
local work=Image{fromFile=out..'source.png'}
local carry=Image{fromFile=out..'carry-proportion-source.png'}

local rows={0,combat.height/5,combat.height*2/5,combat.height*3/5,combat.height*4/5,combat.height}
local workRows={0,256,512,768,1024,1235,1536}
local names={'idle','attack','hit','down','win','weed','scrub','dust','carry','meditate','read'}
local ms={180,100,100,180,180,220,200,220,180,400,300}
local s=Sprite(256,256,ColorMode.RGB);s.layers[1].name='priest'
local sheet=Image(1024,2816,ColorMode.RGB)
for row=0,10 do
 local src=row<5 and combat or work
 local cw=src.width/4
 local y0=row<5 and rows[row+1] or workRows[row-4]
 local y1=row<5 and rows[row+2] or workRows[row-3]
 local factor=row<5 and 0.48 or 0.50
 for col=0,3 do
  local fi=row*4+col+1;if fi>1 then s:newEmptyFrame() end
  s.frames[fi].duration=ms[row+1]/1000
  local frameSrc=src
  local frameEnd=y1
  local frameStart=y0
  local frameX=col*cw
  local frameFactor=factor

  local frameWidth=cw
  if row==8 then
   frameSrc=carry
   frameWidth=carry.width/4
   frameX=col*frameWidth
   frameStart=carry.height/2
   frameEnd=frameStart+carry.height/6
   frameFactor=0.50*1024/carry.width
  end
  if row==1 and col==2 then frameWidth=cw+16 end
  local im=Image(math.floor(frameWidth),math.floor(frameEnd-frameStart),ColorMode.RGB)
  im:drawImage(frameSrc,Point(-math.floor(frameX),-math.floor(frameStart)))
  local x0,ymin,x1,ymax=im.width,im.height,0,0
  for y=0,im.height-1 do for x=0,im.width-1 do
   local px=im:getPixel(x,y);local a=app.pixelColor.rgbaA(px)
   if row==1 and col==3 and x<18 then a=0 end
   if a>127 then
    im:drawPixel(x,y,app.pixelColor.rgba(app.pixelColor.rgbaR(px),app.pixelColor.rgbaG(px),app.pixelColor.rgbaB(px),255))
    x0=math.min(x0,x);ymin=math.min(ymin,y);x1=math.max(x1,x);ymax=math.max(ymax,y)
   else im:drawPixel(x,y,0) end
  end end
  assert(x1>x0,'Empty frame')
  im:resize(math.floor(im.width*frameFactor),math.floor(im.height*frameFactor))
  local dest=Image(256,256,ColorMode.RGB)
  dest:drawImage(im,Point(math.floor(128-(x0+x1)*frameFactor/2),math.floor(170-ymax*frameFactor)))
  s:newCel(s.layers[1],fi,dest,Point(0,0))
  sheet:drawImage(dest,Point(col*256,row*256))
 end
 local tag=s:newTag(row*4+1,row*4+4);tag.name=names[row+1]
end
s:saveAs(out..'priest-complete.aseprite')
sheet:saveAs(out..'priest-complete.png')
