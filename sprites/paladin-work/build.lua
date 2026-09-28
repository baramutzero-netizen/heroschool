local out='D:/heroschool/sprites/paladin-work/'
local src=Image{fromFile=out..'source.png'}
local cw=src.width/4; local ch=src.height/6
local s=Sprite(256,256,ColorMode.RGB)
s.layers[1].name='paladin_and_tools'
local names={'weed','scrub','dust','carry','meditate','read'}
local speeds={220,180,180,180,400,300}
local sheet=Image(1024,1536,ColorMode.RGB)
for row=0,5 do
 for col=0,3 do
  local fi=row*4+col+1
  if fi>1 then s:newEmptyFrame() end
  s.frames[fi].duration=speeds[row+1]/1000
  local im=Image(math.floor(cw),math.floor(ch),ColorMode.RGB)
  im:drawImage(src,Point(-math.floor(col*cw),-math.floor(row*ch)))
  local x0,y0,x1,y1=im.width,im.height,0,0
  for y=0,im.height-1 do for x=0,im.width-1 do
   if app.pixelColor.rgbaA(im:getPixel(x,y))>20 then x0=math.min(x0,x);y0=math.min(y0,y);x1=math.max(x1,x);y1=math.max(y1,y) end
  end end
  assert(x1>x0 and y1>y0,'Empty frame')
  local factor=128/cw
  im:resize(math.floor(im.width*factor),math.floor(im.height*factor))
  local dest=Image(256,256,ColorMode.RGB)
  dest:drawImage(im,Point(math.floor(128-(x0+x1)*factor/2),math.floor(171-y1*factor)))
  s:newCel(s.layers[1],fi,dest,Point(0,0))
  dest:saveAs(out..names[row+1]..'-'..col..'.png')
  sheet:drawImage(dest,Point(col*256,row*256))
 end
 local tag=s:newTag(row*4+1,row*4+4);tag.name=names[row+1]
end
s:saveAs(out..'paladin-work.aseprite')
sheet:saveAs(out..'paladin-work-sheet.png')
print('24 frames, 6 tags exported')
