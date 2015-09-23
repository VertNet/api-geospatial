# Geospatial Quality API

Code for the geospatial quality assessment methods of the VertNet set of APIs.
Author: Javier Otegui

## Usage

### Access

The current base URL for the API is:

	http://api-dev.vertnet-portal.appspot.com/geospatial

although it will surely change in the future.

This URL holds the current (development) version of the API.

Given that it is designed to be an open service to the community, no credentials whatsoever are required. But we reserve the right to close it at any moment if we suspect there is being misuse.

### Input format

This API operates on Primary Biodiversity Records, *i.e.*, the most basic, interpretation-free pieces of information about the occurrence of an organism (taxonomic identification, or "what") in a specific place (geospatial location, or "where") and a moment in time (temporal location, or "when"). It feeds on a single record or a set of records that describe such occurrence. Specifically, the geospatial issues service works with the "what" and the "where", meaning it is more useful if such pieces of information are provided to the API.

While there is no minimum set of required values to pass to the service in order for it to work, the amount of tests to be performed depends on the information provided. One can simply call the base URL and it will return a set of empty fields. To fully leverage the potential of the API, however, a user should send a well-defined set of values. These values must conform to the [DarwinCore Standard](http://rs.tdwg.org/dwc/terms/index.htm), and currently, the API works on these variables:

* [decimalLatitude](http://rs.tdwg.org/dwc/terms/index.htm#decimalLatitude): Value for the Latitude in decimal degrees format (*e.g.* 42.332)
* [decimalLongitude](http://rs.tdwg.org/dwc/terms/index.htm#decimalLongitude): Value for the Longitude in decimal degrees format (*e.g.* -1.833)
* [countryCode](http://rs.tdwg.org/dwc/terms/index.htm#countryCode): 2 character ISO code for the country
* [scientificName](http://rs.tdwg.org/dwc/terms/index.htm#scientificName)

**Caveat**: while the API accepts scientific names as specified in the DarwinCore Standard, currently some tools only work if the "Genus"+"Specific Epithet" binomial is provided in this field. Thus, instead of *"Puma concolor (Linnaeus, 1771)"*, we recommend using just *"Puma concolor"* in the 'scientificName' field.

When working with multiple records (see below how to do this with the POST method), the API accepts more than just these fields. One can send as many key-value pairs as he/she wants, and the API will just by-pass them. They will be presented in the output, though, so it is a good practice to include a field with any type of identification (like an [occurrenceID](http://rs.tdwg.org/dwc/terms/index.htm#occurrenceID)).

### Output format

The output of the API will always be a JSON document, whether it is a single-record or a multi-record assessment. Actually, the API will return the same document that was provided, with the addition of the `flags` element. This new element contains the results of the geospatial and spatio-taxonomic checks the API has performed. The attributes in this `flags` element are one or more of these (depending on the information provided):

* `hasCoordinates`: always. True if coordinates have been sent to the API. False otherwise.
* `hasCountry`: always. True if a country value has been sent to the API. False otherwise.
* `hasScientificName`: always. True if a scientific name has been sent to the API. False otherwise.
* `validCoordinates`: only if `hasCoordinates` is true. True if supplied values conform to the natural limits of coordinates. False otherwise.
* `validCountry`: only if `hasCountry` is true. True if supplied value corresponds to an existing 2-character code for a country. False otherwise.
* `highPrecisionCoordinates`: only if `validCoordinates` is true. True if coordinates have at least 3 decimal figures. False otherwise.
* `nonZeroCoordinates`: only if `validCoordinates` is true. False if both coordinates are 0. True otherwise.
* `coordinatesInsideCountry`: Only if `validCoordinates` and `validCountry` are true. True if coordinates fall inside the specified country. False otherwise.
* `transposedCoordinates`: Only if `coordinatesInsideCountry` is false. True if swapping the coordinates makes them right. False otherwise. This operation can be performed along `negatedLatitude` and `negatedLongitude`.
* `negatedLatitude`: Only if `coordinatesInsideCountry` is false. True if negating the latitude makes coordinates right. False otherwise. This operation can be performed along `transposedCoordinates` and `negatedLongitude`.
* `negatedLongitude`: Only if `coordinatesInsideCountry` is false. True if negating the longitude makes coordinates right. False otherwise. This operation can be performed along `transposedCoordinates` and `negatedLatitude`.
* `distanceToCountryInKm`: Only if `coordinatesInsideCountry`, `transposedCoordinates`, `negatedLatitude` and `negatedLongitude` are false. This will show the distance to the closest point of the country boundaries, in Km.
* `coordinatesInsideRangeMap`: Only if `hasScientificName` and `validCoordinates` are true. True if coordinates fall inside the IUCN range map for the specified species. False otherwise.
* `distanceToRangeMapInKm`: Only if `coordinatesInsideRangeMap` is false. This will show the distance to the closest point of the species range map, in Km.

### Check a single record with `GET`

`GET` requests can be used to assess the quality of a single record. Parameters must be passed urlencoded via the querystring. Here is an example of a working `GET` request:

```bash
curl -H "Content-Type: application/json" "http://api-dev.vertnet-portal.appspot.com/geospatial?decimalLatitude=42.332&decimalLongitude=-1.833&countryCode=ES&scientificName=Puma%20concolor"
```

When using the API in this way, the result is the provided set of values plus the `flags` element, but everything apart from the aforementioned four DarwinCore elements will be ignored. Here is the output of the previous example:

```json
{
	"decimalLatitude": "42.332",
    "decimalLongitude": "-1.833",
	"scientificName": "Puma concolor",
    "countryCode": "ES",
    "flags": {
    	"validCountry": "True",
        "coordinatesInsideCountry": "True",
        "distanceToRangeMapInKm": 6892.799,
        "hasScientificName": "True",
        "nonZeroCoordinates": "True",
        "highPrecisionCoordinates": "True",
        "hasCoordinates": "True",
        "validCoordinates": "True",
        "coordinatesInsideRangeMap": "False",
        "hasCountry": "True"
    }
}
```

### Check multiple records with `POST`

More than one record can be checked in a single request by passing the records in JSON format in the body of a `POST` request. All the records must be wrapped in a list. Here is an example of a working `POST` request:

```json
// body.json
[
    {
        "occurrenceId": 1,
        "decimalLatitude": 42.388,
        "decimalLongitude": -1.833,
        "countryCode": "ES",
        "scientificName": "Abies alba"
    },
    {
        "occurrenceId": 2,
        "decimalLongitude": -1.833,
        "countryCode": "ES",
        "scientificName": "Puma concolor"
    },...
]
```

```bash
curl -H "Content-Type: application/json" -X POST -d @body.json "http://api-dev.vertnet-portal.appspot.com/geospatial"
```

In this case, the extra fields -- like `occurrenceId` -- will not be ignored and will be part of the result.