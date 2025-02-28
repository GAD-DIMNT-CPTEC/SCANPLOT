#! /bin/bash -x

datei=2019111512
datef=2020020212

name=BAM_AVAL

url=https://dataserver.cptec.inpe.br/dataserver_dimnt/das/carlos.bastarz/SCANTEC-2.1.0/dataout/periodo/AVAL_SMNA_V2.3.1

# Forecast days
fctd=11

Regs=(gl hn tr hs as)
Exps=(EXP15 EXP18 X666)
Refs=(ref_era5_no_clim.new ref_gfs_no_clim.new ref_panl_cfsr_clim.new ref_panl_agcm_clim.new ref_panl_no_clim.new)
Ftypes=(field table)

#Regs=(as)
#Exps=(X666)
#Refs=(ref_panl_no_clim.new)
#Ftypes=(table)

echo "sources:" > catalog-scantec_${name}.yml

for reg in ${Regs[@]}
do

    for exp in ${Exps[@]}
    do

      for ref in ${Refs[@]}
      do

        for ftype in ${Ftypes[@]}
        do

          if [ ${ftype} = "field" ]
          then        
                  
            Stats=(VIES RMSE MEAN)

            for stat in ${Stats[@]}
            do
                    
              if [ ${stat} = "VIES" ]; then statn="Bias"; fi
              if [ ${stat} = "RMSE" ]; then statn="Root Mean Square Error"; fi
              if [ ${stat} = "MEAN" ]; then statn="Mean Error"; fi

cat << EOF >> catalog-scantec_${name}.yml

  'scantec-${reg}-${stat,,}-${exp,,}-${ref}-${ftype}':
    args:
      consolidated: true
      urlpath: ${url}/${ref}/${reg}/${stat}${exp}_${datei}${datef}F.zarr 
    description: ${statn} for ${exp} experiment (${reg^^} area - valid for ${datei}-${datef})
    driver: intake_xarray.xzarr.ZarrSource
    metadata: 
      catalog_dir: ${url} 
      tags:
        - atmosphere
        - scantec
        - monan
        - analysis
        - data_assimilation
      region: 
        - ${reg}
      statistic:
        - ${stat,,}
      experiment:
        - ${exp,,}
      reference:
        - ${ref}
      file_type:
        - ${ftype}
      date_initial:
        - ${datei}
      date_final:
        - ${datef}
      forecast_days:
        - ${fctd}
      url: ${url} 

EOF

            done

          elif [ ${ftype} = "table" ]
          then

            Stats=(VIES RMSE ACOR)

            for stat in ${Stats[@]}
            do
                    
              if [ ${stat} = "VIES" ]; then statn="Bias"; fi
              if [ ${stat} = "RMSE" ]; then statn="Root Mean Square Error"; fi
              if [ ${stat} = "ACOR" ]; then statn="Anomaly Correlation"; fi

cat << EOF >> catalog-scantec_${name}.yml

  'scantec-${reg}-${stat,,}-${exp,,}-${ref}-${ftype}':
    args:
      urlpath: ${url}/${ref}/${reg}/${stat}${exp}_${datei}${datef}T.csv 
    description: ${statn} for ${exp} experiment (${reg^^} area - valid for ${datei}-${datef})
    driver: csv
    metadata: 
      catalog_dir: ${url} 
      tags:
        - atmosphere
        - scantec
        - monan
        - analysis
        - data_assimilation
      region: 
        - ${reg}
      statistic:
        - ${stat,,}
      experiment:
        - ${exp,,}
      reference:
        - ${ref}
      file_type:
        - ${ftype}
      date_initial:
        - ${datei}
      date_final:
        - ${datef}
      forecast_days:
        - ${fctd}
      url: ${url} 

EOF

            done

          fi

      done

    done

  done

done

exit 0
