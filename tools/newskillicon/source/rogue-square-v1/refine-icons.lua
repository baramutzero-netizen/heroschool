local root="C:/Users/mjkki/Documents/Codex/2026-09-16/aesprite/outputs/skill-icons/rogue-square-v1/"
local ids={"ambush","weakness","poison","shadow-step","assassination"}
local pc=app.pixelColor
local function visible(p)
 local r,g,b=pc.rgbaR(p),pc.rgbaG(p),pc.rgbaB(p)
 return pc.rgbaA(p)>0
end
local report={}
for _,id in ipairs(ids) do
 local src=app.open(root..id.."-original.png")
 local raw=Image(src.width,src.height,ColorMode.RGB)
 raw:drawSprite(src,1)
 local x0,y0,x1,y1=raw.width,raw.height,-1,-1
 for y=0,raw.height-1 do for x=0,raw.width-1 do
  if visible(raw:getPixel(x,y)) then x0=math.min(x0,x);y0=math.min(y0,y);x1=math.max(x1,x);y1=math.max(y1,y) end
 end end
 local w,h=x1-x0+1,y1-y0+1
 local scale=86/math.max(w,h)
 local dw,dh=math.floor(w*scale+.5),math.floor(h*scale+.5)
 local ox,oy=math.floor((96-dw)/2),math.floor((96-dh)/2)
 local spr=Sprite(96,96,ColorMode.RGB)
 spr.layers[1].name="Transparent canvas"
 local bg=Image(96,96,ColorMode.RGB)
 bg:clear(pc.rgba(0,0,0,0))
 spr:newCel(spr.layers[1],1,bg,Point(0,0))
 local symbol=Image(96,96,ColorMode.RGB)
 for y=0,dh-1 do for x=0,dw-1 do
  local p=raw:getPixel(math.min(x1,x0+math.floor((x+.5)*w/dw)),math.min(y1,y0+math.floor((y+.5)*h/dh)))
  if visible(p) then symbol:drawPixel(x+ox,y+oy,p) end
 end end
 local layer=spr:newLayer()
 layer.name="Skill symbol - 90 percent fill"
 spr:newCel(layer,1,symbol,Point(0,0))
 spr:saveAs(root..id.."-96.aseprite")
 spr:saveCopyAs(root..id.."-96.png")
 local flat=Image(96,96,ColorMode.RGB)
 flat:drawSprite(spr,1)
 local big=Sprite(384,384,ColorMode.RGB)
 local enlarged=Image(384,384,ColorMode.RGB)
 for y=0,383 do for x=0,383 do enlarged:drawPixel(x,y,flat:getPixel(math.floor(x/4),math.floor(y/4))) end end
 big:newCel(big.layers[1],1,enlarged,Point(0,0))
 big:saveCopyAs(root..id.."-4x.png")
 report[#report+1]=id..": content fit "..dw.."x"..dh.." px; canvas 96x96; RGBA; transparent background; no frame"
end
local f=io.open(root.."validation.txt","w")
f:write(table.concat(report,"\n"))
f:close()
print(table.concat(report,"\n"))




