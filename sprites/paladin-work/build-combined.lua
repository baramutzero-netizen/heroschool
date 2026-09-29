local out='D:/heroschool/sprites/paladin-work/'
local combat=Image{fromFile=out..'combat-source.png'}
local work=Image{fromFile=out..'source.png'}
local corrected=Image{fromFile=out..'attack-corrected-source.png'}
local rows={0,246,480,713,909,1145}
local names={'idle','attack','hit','down','win','weed','scrub','dust','carry','meditate','read'}
local ms={180,100,100,180,180,220,200,220,180,400,300}
local s=Sprite(256,256,ColorMode.RGB);s.layers[1].name='paladin'
local sheet=Image(1024,2816,ColorMode.RGB)
for row=0,10 do
 local src=row<5 and combat or work
 local cw=src.width/4
 local y0=row<5 and rows[row+1] or (row-5)*work.height/6
 local y1=row<5 and rows[row+2] or (row-4)*work.height/6
 local factor=row<5 and 0.405 or 0.5
 for col=0,3 do
  local fi=row*4+col+1;if fi>1 then s:newEmptyFrame() end
  s.frames[fi].duration=ms[row+1]/1000
  local frameSrc=src
  local frameEnd=y1
  if row==1 and (col==0 or col==2) then
   frameSrc=corrected
   frameEnd=col==0 and 484 or 490
  end
  local im=Image(math.floor(cw),math.floor(frameEnd-y0),ColorMode.RGB)
  im:drawImage(frameSrc,Point(-math.floor(col*cw),-math.floor(y0)))
  -- The down row extends past y=909 in three columns. Keep only the
  -- connected victory silhouette before measuring bounds or positioning it.
  if row==4 then
   local seen,largest={},{}
   for sy=0,im.height-1 do for sx=0,im.width-1 do
    local key=sy*im.width+sx
    if not seen[key] and app.pixelColor.rgbaA(im:getPixel(sx,sy))>127 then
     local queue={key};local head=1;seen[key]=true
     while head<=#queue do
      local k=queue[head];head=head+1
      local x=k%im.width;local y=math.floor(k/im.width)
      for oy=-1,1 do for ox=-1,1 do
       local nx,ny=x+ox,y+oy;local nk=ny*im.width+nx
       if nx>=0 and nx<im.width and ny>=0 and ny<im.height and not seen[nk] and app.pixelColor.rgbaA(im:getPixel(nx,ny))>127 then
        seen[nk]=true;queue[#queue+1]=nk
       end
      end end
     end
     if #queue>#largest then largest=queue end
    end
   end end
   local keep={};for _,k in ipairs(largest) do keep[k]=true end
   for y=0,im.height-1 do for x=0,im.width-1 do
    if not keep[y*im.width+x] then im:drawPixel(x,y,0) end
   end end
  end
  local x0,ymin,x1,ymax=im.width,im.height,0,0
  for y=0,im.height-1 do for x=0,im.width-1 do
   local px=im:getPixel(x,y);local a=app.pixelColor.rgbaA(px)
   if a>127 then
    im:drawPixel(x,y,app.pixelColor.rgba(app.pixelColor.rgbaR(px),app.pixelColor.rgbaG(px),app.pixelColor.rgbaB(px),255))
    x0=math.min(x0,x);ymin=math.min(ymin,y);x1=math.max(x1,x);ymax=math.max(ymax,y)
   else im:drawPixel(x,y,0) end
  end end
  assert(x1>x0,'Empty frame')
  im:resize(math.floor(im.width*factor),math.floor(im.height*factor))
  local dest=Image(256,256,ColorMode.RGB)
  dest:drawImage(im,Point(math.floor(128-(x0+x1)*factor/2),math.floor(170-ymax*factor)))
  s:newCel(s.layers[1],fi,dest,Point(0,0))
  sheet:drawImage(dest,Point(col*256,row*256))
 end
 local tag=s:newTag(row*4+1,row*4+4);tag.name=names[row+1]
end
s:saveAs(out..'paladin-complete.aseprite')
sheet:saveAs(out..'paladin-complete.png')
