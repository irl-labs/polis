## [MA Master Address Data](https://www.mass.gov/info-details/massgis-data-master-address-data)

Join assessor parcel identifiers with State address list.  Seems too hard.


#### Process

* nomalize_addresses - selected columns from [Advanced Address List](https://www.mass.gov/info-details/massgis-data-master-address-data-advanced-address-list), usps_type conversion, street name exceptions.  Ouput addresses
* LOC_ID_geometry - assessor parcel geometry and address details (streetName, streetNum, unit)
* address_within_parcel - spatial join of [Basic Address Points](https://www.mass.gov/info-details/massgis-data-master-address-data-basic-address-points) within assessor parcel geometry (polygons)
* combine_addresses_parcels

#### Output

* parcel polygon geometry (LOC_ID)
* assessor property identifier (pid)
* [Advanced Address List](https://www.mass.gov/info-details/massgis-data-master-address-data-advanced-address-list) (ADDRESS_ID)



#### Related

* matched on people, property, infrastructure datasets
* what about Dash?
