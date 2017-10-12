load "$NCARG_ROOT/lib/ncarg/nclscripts/contrib/cd_string.ncl"

begin
; Open model level output file

fils = systemfunc ("ls out.nc") ; file paths
f    = addfiles (fils, "r")  
ListSetType (f, "cat")

dbz=f[:]->rxdata 

plot_description="Observed radar reflectivity every 15 minutes"

 lon2d = f[:]->lon2d 
 lat2d = f[:]->lat2d
 time= f[:]->time 
 
dbz@lat2d = lat2d 
dbz@lon2d = lon2d

date=cd_calendar(time,-5)
date_string=tostring(cd_calendar(time, -3))+sprinti("%0.2i", date(:,4))

 delete([/fils, f/])

; create plot

 ResC = True
 ResC@gsnDraw = False
 ResC@gsnFrame = False
 ResC@gsnAddCyclic = False  
 ResC@gsnMaximize   = True         ; Maximize plot in frame.
 ResC@gsnLeftString = ""

 ResC@cnFillOn = True ; do color fill
 ; ResC@cnFillMode = "rasterfill"
 ResC@cnLinesOn=False
 ResC@cnMissingValFillColor = -1

 ResC@mpOutlineOn = True
 ResC@mpFillOn     = True
 ResC@mpLimitMode = "LatLon"                   ;
 ResC@mpMaxLonF    = 15                      ; specify the plot domain
 ResC@mpMinLonF    = 6                      ;
 ResC@mpMinLatF    = 46                     ;
 ResC@mpMaxLatF    = 55                     ;
 ResC@mpDataBaseVersion  = "MediumRes"
 ResC@mpGeophysicalLineThicknessF = 5
 ResC@mpGeophysicalLineColor ="black"
 ResC@mpOutlineBoundarySets = "AllBoundaries"     ; more outlines
 ResC@mpNationalLineThicknessF = 4
 ResC@mpDataSetName         = "Earth..4"     
 ; ResC@mpOutlineOn = True
 ResC@tmXBLabelFontHeightF = 0.01
 ResC@pmTickMarkDisplayMode = True

cmap_r              = read_colormap_file("radar")
cmap_r(0,3)         = 0.0    ; Fully transparent
ResC@cnFillPalette = cmap_r

; ResC@cnFillPalette = "radar_1"
ResC@cnLevelSelectionMode = "ManualLevels"
ResC@cnMinLevelValF = 0
ResC@cnMaxLevelValF = 70 
ResC@cnLevelSpacingF = 5

ResC@lbOrientation = "Vertical"
ResC@pmLabelBarWidthF = 0.05
ResC@gsnLeftString = "RADOLAN"
ResC@gsnRightString = "Copyright DWD"

txres                       = True
txres@txPerimOn             = True
txres@txBackgroundFillColor = "White"
txres@txFontHeightF         = 0.015

amres=True 
amres@amParallelPosF   = -0.5    ; This is the right edge of the plot.
amres@amOrthogonalPosF = 0.5    ; This is the bottom edge of the plot.
amres@amJust = "BottomLeft"

amres2=True 
amres2@amParallelPosF   = -0.5    ; This is the right edge of the plot.
amres2@amOrthogonalPosF = -0.5    ; This is the bottom edge of the plot.
amres2@amJust = "TopLeft"

 do time_i=0,dimsizes(time)-1
 ResC@gsnCenterString= ""+cd_string(time(time_i), "%d %c. %Y")+" at "+cd_string(time(time_i), "%H:%M")+" UTC"
 wks = gsn_open_wks("png","radar_"+date_string(time_i))
 
 plot = gsn_csm_contour_map(wks,dbz(time_i,:,:),ResC)
 text=gsn_create_text(wks, plot_description, txres)
 description=gsn_add_annotation(plot, text, amres)

 id=gsn_add_shapefile_polylines(wks,plot,"$NCARG_ROOT/lib/ncarg/data/shp/DEU_adm1.shp",True)
 draw(plot)
 frame(wks)
end do
end
