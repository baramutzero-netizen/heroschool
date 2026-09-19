-- Aseprite --batch --script sprites/build_frames.lua
local root=app.params.root or 'D:/heroschool/sprites/'
local input=io.open(root..'frames-v3/import.json','r')
local data=json.decode(input:read('*a')); input:close()
local cache={}
local function source(path)
 if not cache[path] then
  local s=app.open(root..path)
  cache[path]=s.cels[1].image:clone(); s:close()
 end
 return cache[path]
end
local function saveImage(im,path)
 local s=Sprite(im.width,im.height,ColorMode.RGB)
 s:newCel(s.layers[1],1,im,Point(0,0)); s:saveCopyAs(path); s:close()
end
local summary={version=3,canvas={256,256},pivot={128,170},logicalSize={128,128},margin=data.margin,jobs={}}
for job,info in pairs(data.jobs) do
 local dir=root..'frames-v3/'..job
 app.fs.makeAllDirectories(dir)
 local anim=Sprite(256,256,ColorMode.RGB)
 anim.layers[1].name='Character'
 local fxLayer=anim:newLayer(); fxLayer.name='Local effect'
 local atlas=Image(256*6,256*5,ColorMode.RGB)
 local out={frames={},counts={4,6,3,5,4}}
 local rows={idle=0,attack=1,hit=2,down=3,win=4}
 local starts={}; local ends={}
 for i,f in ipairs(info.frames) do
  local raw=source(f.source); local b=f.box
  local crop=Image(b[3]-b[1],b[4]-b[2],ColorMode.RGB)
  for _,run in ipairs(f.runs) do
   for x=run[2],run[3]-1 do
    local c=raw:getPixel(x,run[1])
    crop:drawPixel(x-b[1],run[1]-b[2],app.pixelColor.rgba(app.pixelColor.rgbaR(c),app.pixelColor.rgbaG(c),app.pixelColor.rgbaB(c),255))
   end
  end
  crop:resize(math.max(1,math.floor(crop.width*f.scale+.5)),math.max(1,math.floor(crop.height*f.scale+.5)))
  local dx=math.floor(data.pivot[1]-(f.anchor[1]-b[1])*f.scale+.5)
  local dy=math.floor(data.pivot[2]-(f.anchor[2]-b[2])*f.scale+.5)
  assert(dx>=16 and dy>=16 and dx+crop.width<=240 and dy+crop.height<=240,job..' '..f.motion..f.frame..' exceeds safe canvas')
  local full=Image(256,256,ColorMode.RGB); full:drawImage(crop,Point(dx,dy))
  local body=full:clone(); local effect=Image(256,256,ColorMode.RGB)
  -- Detached rogue strikes are an effect, not a moving body/pivot.
  if job=='rogue' and f.motion=='attack' and (f.sourcePose==2 or f.sourcePose==3) then
   effect=full:clone(); body:clear()
  elseif f.motion=='attack' and job=='ninja' then
   -- Water hue is distinct from the dark indigo costume and skin.
   for it in body:pixels() do
    local c=it(); local r=app.pixelColor.rgbaR(c); local g=app.pixelColor.rgbaG(c); local blue=app.pixelColor.rgbaB(c)
    if app.pixelColor.rgbaA(c)>0 and blue>125 and g>60 and blue-r>70 and it.y>130 then effect:drawPixel(it.x,it.y,c); it(0) end
   end
  end
  local stem=f.motion..'-'..string.format('%02d',f.frame)
  saveImage(body,dir..'/'..stem..'.png')
  saveImage(effect,dir..'/'..stem..'.fx.png')
  if i>1 then anim:newEmptyFrame() end
  anim:newCel(anim.layers[1],i,body,Point(0,0)); anim:newCel(fxLayer,i,effect,Point(0,0)); anim.frames[i].duration=f.duration/1000
  starts[f.motion]=starts[f.motion] or i; ends[f.motion]=i
  atlas:drawImage(full,Point(f.frame*256,rows[f.motion]*256))
  table.insert(out.frames,{motion=f.motion,frame=f.frame,file=job..'/'..stem..'.png',effect=job..'/'..stem..'.fx.png',duration=f.duration,pivot={128,170},bounds={dx,dy,dx+crop.width,dy+crop.height}})
 end
 for m,start in pairs(starts) do local tag=anim:newTag(start,ends[m]); tag.name=m end
 anim:saveAs(dir..'/'..job..'.aseprite'); anim:close()
 saveImage(atlas,dir..'/'..job..'-sheet.png')
 summary.jobs[job]=out
 print(job..' 22 frames, fixed pivot 128,170')
end
local output=io.open(root..'frames-v3/manifest.json','w'); output:write(json.encode(summary)); output:close()
