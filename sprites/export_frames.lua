-- Export edited .aseprite files without re-importing the old source sheets.
-- aseprite -b --script-param root=D:/heroschool/sprites/ --script sprites/export_frames.lua
local root=app.params.root or 'D:/heroschool/sprites/'
local input=assert(io.open(root..'frames-v3/manifest.json','r'))
local data=json.decode(input:read('*a')); input:close()
local output={version=3,canvas={256,256},logicalSize={128,128},pivot={128,170},margin=16,jobs={}}
local function save(im,path)
 local tmp=Sprite(256,256,ColorMode.RGB)
 tmp:newCel(tmp.layers[1],1,im,Point(0,0)); tmp:saveCopyAs(path); tmp:close()
end
for job,info in pairs(data.jobs) do
 local sprite=assert(app.open(root..'frames-v3/'..job..'/'..job..'.aseprite'))
 assert(sprite.width==256 and sprite.height==256,job..': canvas must be 256x256')
 assert(#sprite.frames==#info.frames,job..': update manifest when adding/removing frames')
 assert(#sprite.tags==5,job..': five motion tags required')
 local out={counts={},frames={}}
 for _,count in ipairs(info.counts) do table.insert(out.counts,count) end
 for i,f in ipairs(info.frames) do
  local body=Image(256,256,ColorMode.RGB); local fx=Image(256,256,ColorMode.RGB)
  for _,cel in ipairs(sprite.cels) do
   if cel.frame.frameNumber==i then
    if cel.layer.name=='Character' then body:drawImage(cel.image,cel.position)
    elseif cel.layer.name=='Local effect' then fx:drawImage(cel.image,cel.position)
    else error(job..': unsupported layer '..cel.layer.name) end
   end
  end
  local bounds={256,256,0,0}
  for _,im in ipairs({body,fx}) do
   for it in im:pixels() do
    local a=app.pixelColor.rgbaA(it())
    assert(a==0 or a==255,job..' '..f.file..': nonbinary alpha')
    if a>0 then
     assert(it.x>=16 and it.x<240 and it.y>=16 and it.y<240,job..' '..f.file..': safe border')
     bounds[1]=math.min(bounds[1],it.x); bounds[2]=math.min(bounds[2],it.y)
     bounds[3]=math.max(bounds[3],it.x+1); bounds[4]=math.max(bounds[4],it.y+1)
    end
   end
  end
  assert(bounds[3]>0,job..' '..f.file..': empty frame')
  save(body,root..'frames-v3/'..f.file); save(fx,root..'frames-v3/'..f.effect)
  table.insert(out.frames,{motion=f.motion,frame=f.frame,file=f.file,effect=f.effect,
   duration=math.floor(sprite.frames[i].duration*1000+.5),pivot={128,170},bounds=bounds})
 end
 output.jobs[job]=out; sprite:close(); print(job..': editable layers verified and exported')
end
local file=assert(io.open(root..'frames-v3/manifest.json','w'))
file:write(json.encode(output)); file:close()
