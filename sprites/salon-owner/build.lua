local out='D:/heroschool/sprites/salon-owner/'
local src=Image{fromFile=out..'snip-source.png'}
local s=Sprite(256,256,ColorMode.RGB)
local atlas=Image(1024,256,ColorMode.RGB)
for i=0,3 do
 if i>0 then s:newEmptyFrame() end
 s.frames[i+1].duration=0.2
 local w,h=math.floor(src.width/2),math.floor(src.height/2)
 local im=Image(w,h,ColorMode.RGB)
 im:drawImage(src,Point(-(i%2)*w,-math.floor(i/2)*h))
 local bottom=0
 for y=0,h-1 do for x=0,w-1 do
  local p=im:getPixel(x,y)
  if app.pixelColor.rgbaA(p)>127 then bottom=math.max(bottom,y) else im:drawPixel(x,y,0) end
 end end
 local factor=0.35
 im:resize(math.floor(w*factor),math.floor(h*factor))
 local frame=Image(256,256,ColorMode.RGB)
 frame:drawImage(im,Point(18,math.floor(238-bottom*im.height/h)))
 s:newCel(s.layers[1],i+1,frame)
 atlas:drawImage(frame,Point(i*256,0))
end
local tag=s:newTag(1,4);tag.name='snip'
s:saveAs(out..'snip.aseprite')
atlas:saveAs(out..'snip.png')
