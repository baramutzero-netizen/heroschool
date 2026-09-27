local out='D:/heroschool/sprites/avatar-lab/'
local s=Sprite(256,256,ColorMode.RGB)
local specs={{'cape_back','망토'}, {'hair_back','헤어 뒤'}, {'body','공통 몸체'}, {'pants','하의'}, {'shoes','신발'}, {'top','상의'}, {'arm_back','뒤 팔'}, {'head','공통 머리'}, {'face','눈+입'}, {'arm_front','앞 팔'}, {'gloves','장갑'}, {'hair_front','헤어 앞'}, {'hat','모자'}}
local layers={}
for i,v in ipairs(specs) do local l=i==1 and s.layers[1] or s:newLayer();l.name=v[1];layers[v[1]]=l end
local function c(h) return app.pixelColor.rgba(tonumber(h:sub(1,2),16),tonumber(h:sub(3,4),16),tonumber(h:sub(5,6),16),255) end
local ink=c('493b46');local skin=c('f6cfb0');local shade=c('c9937d');local light=c('ffe5c9');local cloth=c('6c8392');local edge=c('334656');local gold=c('d8b574')
local im
local function rect(x,y,w,h,col) for yy=y,y+h-1 do for xx=x,x+w-1 do im:drawPixel(xx,yy,col) end end end
local function ell(x,y,w,h,col) for yy=y,y+h-1 do for xx=x,x+w-1 do if ((xx-x+.5)/w*2-1)^2+((yy-y+.5)/h*2-1)^2<=1 then im:drawPixel(xx,yy,col) end end end end
local function poly(pts,col) for y=0,255 do for x=0,255 do local hit=false;local j=#pts;for i=1,#pts do local a,b=pts[i],pts[j];if (a[2]>y)~=(b[2]>y) and x<(b[1]-a[1])*(y-a[2])/(b[2]-a[2])+a[1] then hit=not hit end;j=i end;if hit then im:drawPixel(x,y,col) end end end end
local base={}
for _,v in ipairs(specs) do
 im=Image(256,256,ColorMode.RGB);local k=v[1]
 if k=='head' then ell(110,80,39,39,ink);ell(111,81,37,36,shade);ell(112,81,35,33,skin);ell(115,83,28,23,light);ell(108,99,7,11,shade);ell(109,99,5,8,skin)
 elseif k=='body' then rect(124,113,10,9,shade);ell(117,117,26,28,ink);ell(119,118,22,25,skin);rect(120,141,9,25,shade);rect(132,141,9,25,shade);rect(121,143,6,22,skin);rect(134,143,6,22,skin);rect(119,137,23,10,edge);rect(120,138,21,7,cloth)
 elseif k=='face' then rect(119,99,7,2,ink);rect(137,99,7,2,ink);ell(120,101,6,9,ink);ell(138,101,6,9,ink);rect(121,102,3,5,c('537c9c'));rect(139,102,3,5,c('537c9c'));rect(121,101,2,2,c('ffffff'));rect(139,101,2,2,c('ffffff'));rect(130,113,5,1,shade)
 elseif k=='arm_back' then ell(111,119,9,22,ink);ell(112,120,7,20,skin);ell(109,137,9,8,shade);ell(110,137,7,6,skin)
 elseif k=='arm_front' then ell(141,119,9,22,ink);ell(142,120,7,20,skin);ell(143,137,9,8,shade);ell(144,137,7,6,skin)
 elseif k=='pants' then rect(119,140,23,10,edge);rect(120,141,21,7,cloth);rect(119,149,10,8,edge);rect(132,149,10,8,edge);rect(121,149,6,6,cloth);rect(134,149,6,6,cloth)
 elseif k=='shoes' then ell(116,160,14,11,edge);ell(132,160,15,11,edge);rect(118,160,10,5,c('78665a'));rect(134,160,10,5,c('78665a'));rect(116,168,14,3,ink);rect(132,168,15,3,ink);rect(120,162,7,1,gold);rect(136,162,7,1,gold)
 elseif k=='top' then poly({{118,117},{125,117},{130,122},{135,117},{142,119},{144,142},{117,142}},edge);poly({{120,119},{125,120},{130,126},{136,119},{140,121},{141,139},{120,139}},cloth);rect(128,126,2,13,gold);rect(119,138,22,3,c('57473e'));rect(128,137,5,4,gold)
 elseif k=='gloves' then ell(109,137,9,9,edge);ell(143,137,10,9,edge);rect(110,137,7,2,gold);rect(144,137,8,2,gold)
 elseif k=='cape_back' then poly({{117,117},{140,117},{151,160},{109,160}},edge);poly({{119,119},{138,119},{148,157},{113,157}},c('53687d'));poly({{119,122},{123,121},{120,157},{115,157}},c('7b8fa0'));rect(114,157,34,2,gold)
 elseif k=='hair_back' then ell(106,77,46,52,c('715342'));ell(108,78,42,48,c('ae8055'))
 elseif k=='hair_front' then ell(109,77,42,24,c('715342'));ell(110,78,40,21,c('d4ab72'));poly({{112,85},{146,84},{145,100},{139,94},{136,99},{129,90},{123,101},{120,94},{113,100}},c('d4ab72'));rect(115,82,17,2,c('f1d09a'));rect(111,94,4,17,c('ae8055'))
 elseif k=='hat' then poly({{109,83},{115,73},{140,73},{149,84}},edge);poly({{113,81},{118,75},{138,75},{145,81}},cloth);rect(108,83,42,4,edge);rect(111,83,36,2,gold);ell(129,76,5,5,gold)
 end
 base[k]=im
end
-- Every articulated part has its own source mask. Never branch on destination x:
-- rotating across that boundary used to leave a second glove behind.
local function mask(src,x0,y0,x1,y1)
 local t=Image(256,256,ColorMode.RGB)
 for y=y0,y1 do for x=x0,x1 do t:drawPixel(x,y,src:getPixel(x,y)) end end
 return t
end
local actions={{'idle',4,180},{'attack',6,100},{'hit',3,110},{'down',5,160},{'win',4,180},
 {'swing_one',8,90},{'swing_two',10,90},{'shoot_gun',6,110},{'shoot_bow',8,120},{'lie',8,150}}
-- dx, dy, torso lean, front-arm angle, rear-arm angle, leg spread, root rotation
local poses={
 idle={{0,0,0,0,0,0},{0,-1,0,.03,-.03,0},{0,0,0,0,0,0},{0,1,0,-.03,.03,0}},
 attack={{0,0,0,0,0,0},{-3,2,-.12,.6,-.2,.1},{6,0,.2,-1.3,-.3,.25},{9,1,.27,-1.65,-.4,.3},{4,0,.1,-.8,-.2,.12},{0,0,0,0,0,0}},
 hit={{-3,1,-.15,.3,-.3,.1},{-6,3,-.25,.5,-.5,.2},{0,0,0,0,0,0}},
 down={{0,0,0,0,0,0,0},{-6,1,0,.3,-.2,.1,.3},{-15,1,0,.6,-.4,.1,.7},{-25,0,0,.8,-.5,0,1.2},{-34,-1,0,.3,-.2,0,1.57}},
 win={{0,1,0,-.4,.3,.1},{0,-7,-.08,-2.6,2.5,.18},{0,-4,.08,-2.8,2.7,.12},{0,0,0,-2.5,2.5,0}},
 swing_one={{0,0,0,0,0,0},{-4,3,-.2,.7,-.3,.15},{-6,2,-.3,2.8,-.5,.22},{2,-3,-.05,3.7,-.7,.3},{12,1,.32,4.7,-.6,.4},{15,3,.4,5.6,-.3,.4},{6,1,.15,6.1,-.1,.15},{0,0,0,6.28,0,0}},
 swing_two={{0,0,0,0,0,0},{-2,4,-.12,-.7,.7,.15},{-4,3,-.23,-2.6,2.6,.25},{-3,-2,-.18,-2.9,2.9,.22},{2,-6,0,-3.3,3.2,.1},{10,2,.3,-4.8,4.8,.35},{12,5,.4,-5.4,5.4,.42},{8,3,.25,-5.8,5.8,.3},{3,1,.1,-6.1,6.1,.1},{0,0,0,-6.28,6.28,0}},
 shoot_gun={{0,0,0,0,0,0},{1,2,.08,-1.4,-1.1,.2},{3,1,.12,-1.57,-1.25,.3},{-5,0,-.13,-1.85,-1.5,.3},{-2,1,-.05,-1.6,-1.25,.2},{0,0,0,0,0,0}},
 shoot_bow={{0,0,0,0,0,0},{-1,2,-.08,-1.1,.4,.15},{-3,1,-.13,-1.5,1.1,.25},{-5,0,-.19,-1.57,1.7,.3},{-5,0,-.2,-1.57,1.85,.3},{3,0,.08,-1.5,2.25,.3},{1,1,.04,-1,.8,.15},{0,0,0,0,0,0}},
 lie={{0,0,0,0,0,0,0},{-2,5,-.1,.2,-.2,.25,0},{-8,6,0,.6,-.4,.2,.3},{-18,3,0,.8,-.5,.1,.8},{-28,0,0,.3,-.2,0,1.3},{-34,-1,0,0,0,0,1.57},{-34,-1,0,0,0,0,1.57},{-34,-1,0,0,0,0,1.57}}
}
-- Compact key poses: anticipation, action, follow-through (and recovery when useful).
local picks={idle={1,2,4},attack={2,4,5,6},hit={1,2,3},down={1,3,5},win={1,2,4},swing_one={3,5,6,8},swing_two={4,6,7,10},shoot_gun={2,3,4,6},shoot_bow={3,5,6,8},lie={1,3,5,8}}
local timing={idle={240,240,240},attack={180,90,160,180},hit={90,170,180},down={130,150,500},win={150,250,350},swing_one={230,80,170,180},swing_two={260,90,190,180},shoot_gun={200,100,130,220},shoot_bow={180,260,90,220},lie={150,200,200,600}}
for _,a in ipairs(actions) do local compact={};for _,i in ipairs(picks[a[1]]) do compact[#compact+1]=poses[a[1]][i] end;poses[a[1]]=compact;a[2]=#compact end
local function inv(x,y,px,py,an)
 local ox,oy=x-px,y-py;return px+ox*math.cos(an)+oy*math.sin(an),py-ox*math.sin(an)+oy*math.cos(an)
end
local fi=0
for _,a in ipairs(actions) do local start=fi+1
 for f=1,a[2] do
  fi=fi+1;if fi>1 then s:newEmptyFrame() end;s.frames[fi].duration=timing[a[1]][f]/1000
  local pose=poses[a[1]][f];local dx,dy,lean,front,back,spread,roll=table.unpack(pose);roll=roll or 0
  for _,v in ipairs(specs) do local k=v[1];local dest=Image(256,256,ColorMode.RGB)
   local pieces={}
   if k=='gloves' then pieces={{mask(base[k],0,0,130,255),'back'},{mask(base[k],131,0,255,255),'front'}}
   elseif k=='arm_front' then pieces={{base[k],'front'}}
   elseif k=='arm_back' then pieces={{base[k],'back'}}
   elseif k=='body' or k=='pants' or k=='shoes' then
    pieces={{mask(base[k],0,0,255,145),'upper'},{mask(base[k],0,146,130,255),'legL'},{mask(base[k],131,146,255,255),'legR'}}
   else pieces={{base[k],'upper'}} end
   for _,piece in ipairs(pieces) do local src,part=piece[1],piece[2]
    for y=0,255 do for x=0,255 do
     local xx,yy=inv(x-dx,y-dy,128,164,roll)
     if part=='legL' then xx,yy=inv(xx,yy,124,145,spread)
     elseif part=='legR' then xx,yy=inv(xx,yy,136,145,-spread)
     else
      xx,yy=inv(xx,yy,130,143,-lean)
      if part=='front' then xx,yy=inv(xx,yy,145,121,front)
      elseif part=='back' then xx,yy=inv(xx,yy,115,121,back) end
     end
     xx=math.floor(xx+.5);yy=math.floor(yy+.5)
     if xx>=0 and xx<256 and yy>=0 and yy<256 then local pixel=src:getPixel(xx,yy);if app.pixelColor.rgbaA(pixel)>0 then dest:drawPixel(x,y,pixel) end end
    end end
   end
   s:newCel(layers[k],fi,dest,Point(0,0))
  end
 end
 local tag=s:newTag(start,fi);tag.name=a[1]
end
local first=1;for j,a in ipairs(actions) do s.tags[j].fromFrame=first;s.tags[j].toFrame=first+a[2]-1;first=first+a[2] end
s:saveAs(out..'common-avatar-sample.aseprite')
-- Export aligned layer sheets; no trimming, identical 6-column layout.
for _,v in ipairs(specs) do
 for _,l in ipairs(s.layers) do l.isVisible=l.name==v[1] end
 app.command.ExportSpriteSheet{ui=false,type=SpriteSheetType.ROWS,columns=6,textureFilename=out..v[1]..'.png',dataFilename='',listLayers=false,listTags=false}
end
for _,l in ipairs(s.layers) do l.isVisible=true end
s:saveAs(out..'common-avatar-sample.aseprite')
app.command.ExportSpriteSheet{ui=false,type=SpriteSheetType.ROWS,columns=6,textureFilename=out..'sample-sheet.png',dataFilename=out..'sample-sheet.json',listLayers=true,listTags=true}
print('Created '..#s.frames..' frames / '..#s.layers..' layers')

local guide=s:newLayer();guide.name='guide_origin_128_171';guide.isVisible=false;guide.isEditable=false
local g=Image(256,256,ColorMode.RGB);for x=96,160 do g:drawPixel(x,171,app.pixelColor.rgba(90,200,130,180)) end;for y=76,178 do g:drawPixel(128,y,app.pixelColor.rgba(90,200,130,180)) end;s:newCel(guide,1,g)
s:saveAs(out..'common-avatar-sample.aseprite')
