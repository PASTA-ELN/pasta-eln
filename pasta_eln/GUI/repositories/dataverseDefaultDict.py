DATAVERSE_METADATA = {
  "datasetVersion": {
    "license": {
      "name": "CC0 1.0",
      "uri": "http://creativecommons.org/publicdomain/zero/1.0"
    },
    "metadataBlocks": {
      "citation": {
        "displayName": "Citation Metadata",
        "fields": [
          {
            "typeName": "title",
            "multiple": False,
            "typeClass": "primitive",
            "value": "Replication Data for: Title"
          },
          {
            "typeName": "subtitle",
            "multiple": False,
            "typeClass": "primitive",
            "value": "Subtitle"
          },
          {
            "typeName": "alternativeTitle",
            "multiple": False,
            "typeClass": "primitive",
            "value": "Alternative Title"
          },
          {
            "typeName": "alternativeURL",
            "multiple": False,
            "typeClass": "primitive",
            "value": "http://AlternativeURL.org"
          },
          {
            "typeName": "otherId",
            "multiple": True,
            "typeClass": "compound",
            "value": [
              {
                "otherIdAgency": {
                  "typeName": "otherIdAgency",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "OtherIDAgency1"
                },
                "otherIdValue": {
                  "typeName": "otherIdValue",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "OtherIDIdentifier1"
                }
              },
              {
                "otherIdAgency": {
                  "typeName": "otherIdAgency",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "OtherIDAgency2"
                },
                "otherIdValue": {
                  "typeName": "otherIdValue",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "OtherIDIdentifier2"
                }
              }
            ]
          },
          {
            "typeName": "author",
            "multiple": True,
            "typeClass": "compound",
            "value": [
              {
                "authorName": {
                  "typeName": "authorName",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "LastAuthor1, FirstAuthor1"
                },
                "authorAffiliation": {
                  "typeName": "authorAffiliation",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "AuthorAffiliation1"
                },
                "authorIdentifierScheme": {
                  "typeName": "authorIdentifierScheme",
                  "multiple": False,
                  "typeClass": "controlledVocabulary",
                  "value": "ORCID"
                },
                "authorIdentifier": {
                  "typeName": "authorIdentifier",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "AuthorIdentifier1"
                }
              },
              {
                "authorName": {
                  "typeName": "authorName",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "LastAuthor2, FirstAuthor2"
                },
                "authorAffiliation": {
                  "typeName": "authorAffiliation",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "AuthorAffiliation2"
                },
                "authorIdentifierScheme": {
                  "typeName": "authorIdentifierScheme",
                  "multiple": False,
                  "typeClass": "controlledVocabulary",
                  "value": "ISNI"
                },
                "authorIdentifier": {
                  "typeName": "authorIdentifier",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "AuthorIdentifier2"
                }
              }
            ]
          },
          {
            "typeName": "datasetContact",
            "multiple": True,
            "typeClass": "compound",
            "value": [
              {
                "datasetContactName": {
                  "typeName": "datasetContactName",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "LastContact1, FirstContact1"
                },
                "datasetContactAffiliation": {
                  "typeName": "datasetContactAffiliation",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "ContactAffiliation1"
                },
                "datasetContactEmail": {
                  "typeName": "datasetContactEmail",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "ContactEmail1@mailinator.com"
                }
              },
              {
                "datasetContactName": {
                  "typeName": "datasetContactName",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "LastContact2, FirstContact2"
                },
                "datasetContactAffiliation": {
                  "typeName": "datasetContactAffiliation",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "ContactAffiliation2"
                },
                "datasetContactEmail": {
                  "typeName": "datasetContactEmail",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "ContactEmail2@mailinator.com"
                }
              }
            ]
          },
          {
            "typeName": "dsDescription",
            "multiple": True,
            "typeClass": "compound",
            "value": [
              {
                "dsDescriptionValue": {
                  "typeName": "dsDescriptionValue",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "DescriptionText1"
                },
                "dsDescriptionDate": {
                  "typeName": "dsDescriptionDate",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "1000-01-01"
                }
              },
              {
                "dsDescriptionValue": {
                  "typeName": "dsDescriptionValue",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "DescriptionText2"
                },
                "dsDescriptionDate": {
                  "typeName": "dsDescriptionDate",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "1000-02-02"
                }
              }
            ]
          },
          {
            "typeName": "subject",
            "multiple": True,
            "typeClass": "controlledVocabulary",
            "value": [
              "Agricultural Sciences",
              "Business and Management",
              "Engineering",
              "Law"
            ]
          },
          {
            "typeName": "keyword",
            "multiple": True,
            "typeClass": "compound",
            "value": [
              {
                "keywordValue": {
                  "typeName": "keywordValue",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "KeywordTerm1"
                },
                "keywordVocabulary": {
                  "typeName": "keywordVocabulary",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "KeywordVocabulary1"
                },
                "keywordVocabularyURI": {
                  "typeName": "keywordVocabularyURI",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "http://KeywordVocabularyURL1.org"
                }
              },
              {
                "keywordValue": {
                  "typeName": "keywordValue",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "KeywordTerm2"
                },
                "keywordVocabulary": {
                  "typeName": "keywordVocabulary",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "KeywordVocabulary2"
                },
                "keywordVocabularyURI": {
                  "typeName": "keywordVocabularyURI",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "http://KeywordVocabularyURL2.org"
                }
              }
            ]
          },
          {
            "typeName": "topicClassification",
            "multiple": True,
            "typeClass": "compound",
            "value": [
              {
                "topicClassValue": {
                  "typeName": "topicClassValue",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "Topic Classification Term1"
                },
                "topicClassVocab": {
                  "typeName": "topicClassVocab",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "Topic Classification Vocab1"
                },
                "topicClassVocabURI": {
                  "typeName": "topicClassVocabURI",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "https://TopicClassificationURL1.com"
                }
              },
              {
                "topicClassValue": {
                  "typeName": "topicClassValue",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "Topic Classification Term2"
                },
                "topicClassVocab": {
                  "typeName": "topicClassVocab",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "Topic Classification Vocab2"
                },
                "topicClassVocabURI": {
                  "typeName": "topicClassVocabURI",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "https://TopicClassificationURL2.com"
                }
              }
            ]
          },
          {
            "typeName": "publication",
            "multiple": True,
            "typeClass": "compound",
            "value": [
              {
                "publicationCitation": {
                  "typeName": "publicationCitation",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "RelatedPublicationCitation1"
                },
                "publicationIDType": {
                  "typeName": "publicationIDType",
                  "multiple": False,
                  "typeClass": "controlledVocabulary",
                  "value": "ark"
                },
                "publicationIDNumber": {
                  "typeName": "publicationIDNumber",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "RelatedPublicationIDNumber1"
                },
                "publicationURL": {
                  "typeName": "publicationURL",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "http://RelatedPublicationURL1.org"
                }
              },
              {
                "publicationCitation": {
                  "typeName": "publicationCitation",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "RelatedPublicationCitation2"
                },
                "publicationIDType": {
                  "typeName": "publicationIDType",
                  "multiple": False,
                  "typeClass": "controlledVocabulary",
                  "value": "arXiv"
                },
                "publicationIDNumber": {
                  "typeName": "publicationIDNumber",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "RelatedPublicationIDNumber2"
                },
                "publicationURL": {
                  "typeName": "publicationURL",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "http://RelatedPublicationURL2.org"
                }
              }
            ]
          },
          {
            "typeName": "notesText",
            "multiple": False,
            "typeClass": "primitive",
            "value": "Notes1"
          },
          {
            "typeName": "language",
            "multiple": True,
            "typeClass": "controlledVocabulary",
            "value": [
              "Abkhaz",
              "Afar"
            ]
          },
          {
            "typeName": "producer",
            "multiple": True,
            "typeClass": "compound",
            "value": [
              {
                "producerName": {
                  "typeName": "producerName",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "LastProducer1, FirstProducer1"
                },
                "producerAffiliation": {
                  "typeName": "producerAffiliation",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "ProducerAffiliation1"
                },
                "producerAbbreviation": {
                  "typeName": "producerAbbreviation",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "ProducerAbbreviation1"
                },
                "producerURL": {
                  "typeName": "producerURL",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "http://ProducerURL1.org"
                },
                "producerLogoURL": {
                  "typeName": "producerLogoURL",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "http://ProducerLogoURL1.org"
                }
              },
              {
                "producerName": {
                  "typeName": "producerName",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "LastProducer2, FirstProducer2"
                },
                "producerAffiliation": {
                  "typeName": "producerAffiliation",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "ProducerAffiliation2"
                },
                "producerAbbreviation": {
                  "typeName": "producerAbbreviation",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "ProducerAbbreviation2"
                },
                "producerURL": {
                  "typeName": "producerURL",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "http://ProducerURL2.org"
                },
                "producerLogoURL": {
                  "typeName": "producerLogoURL",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "http://ProducerLogoURL2.org"
                }
              }
            ]
          },
          {
            "typeName": "productionDate",
            "multiple": False,
            "typeClass": "primitive",
            "value": "1003-01-01"
          },
          {
            "typeName": "productionPlace",
            "multiple": True,
            "typeClass": "primitive",
            "value": [
              "ProductionPlace"
            ]
          },
          {
            "typeName": "contributor",
            "multiple": True,
            "typeClass": "compound",
            "value": [
              {
                "contributorType": {
                  "typeName": "contributorType",
                  "multiple": False,
                  "typeClass": "controlledVocabulary",
                  "value": "Data Collector"
                },
                "contributorName": {
                  "typeName": "contributorName",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "LastContributor1, FirstContributor1"
                }
              },
              {
                "contributorType": {
                  "typeName": "contributorType",
                  "multiple": False,
                  "typeClass": "controlledVocabulary",
                  "value": "Data Curator"
                },
                "contributorName": {
                  "typeName": "contributorName",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "LastContributor2, FirstContributor2"
                }
              }
            ]
          },
          {
            "typeName": "grantNumber",
            "multiple": True,
            "typeClass": "compound",
            "value": [
              {
                "grantNumberAgency": {
                  "typeName": "grantNumberAgency",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "GrantInformationGrantAgency1"
                },
                "grantNumberValue": {
                  "typeName": "grantNumberValue",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "GrantInformationGrantNumber1"
                }
              },
              {
                "grantNumberAgency": {
                  "typeName": "grantNumberAgency",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "GrantInformationGrantAgency2"
                },
                "grantNumberValue": {
                  "typeName": "grantNumberValue",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "GrantInformationGrantNumber2"
                }
              }
            ]
          },
          {
            "typeName": "distributor",
            "multiple": True,
            "typeClass": "compound",
            "value": [
              {
                "distributorName": {
                  "typeName": "distributorName",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "LastDistributor1, FirstDistributor1"
                },
                "distributorAffiliation": {
                  "typeName": "distributorAffiliation",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "DistributorAffiliation1"
                },
                "distributorAbbreviation": {
                  "typeName": "distributorAbbreviation",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "DistributorAbbreviation1"
                },
                "distributorURL": {
                  "typeName": "distributorURL",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "http://DistributorURL1.org"
                },
                "distributorLogoURL": {
                  "typeName": "distributorLogoURL",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "http://DistributorLogoURL1.org"
                }
              },
              {
                "distributorName": {
                  "typeName": "distributorName",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "LastDistributor2, FirstDistributor2"
                },
                "distributorAffiliation": {
                  "typeName": "distributorAffiliation",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "DistributorAffiliation2"
                },
                "distributorAbbreviation": {
                  "typeName": "distributorAbbreviation",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "DistributorAbbreviation2"
                },
                "distributorURL": {
                  "typeName": "distributorURL",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "http://DistributorURL2.org"
                },
                "distributorLogoURL": {
                  "typeName": "distributorLogoURL",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "http://DistributorLogoURL2.org"
                }
              }
            ]
          },
          {
            "typeName": "distributionDate",
            "multiple": False,
            "typeClass": "primitive",
            "value": "1004-01-01"
          },
          {
            "typeName": "depositor",
            "multiple": False,
            "typeClass": "primitive",
            "value": "LastDepositor, FirstDepositor"
          },
          {
            "typeName": "dateOfDeposit",
            "multiple": False,
            "typeClass": "primitive",
            "value": "1002-01-01"
          },
          {
            "typeName": "timePeriodCovered",
            "multiple": True,
            "typeClass": "compound",
            "value": [
              {
                "timePeriodCoveredStart": {
                  "typeName": "timePeriodCoveredStart",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "1005-01-01"
                },
                "timePeriodCoveredEnd": {
                  "typeName": "timePeriodCoveredEnd",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "1005-01-02"
                }
              },
              {
                "timePeriodCoveredStart": {
                  "typeName": "timePeriodCoveredStart",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "1005-02-01"
                },
                "timePeriodCoveredEnd": {
                  "typeName": "timePeriodCoveredEnd",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "1005-02-02"
                }
              }
            ]
          },
          {
            "typeName": "dateOfCollection",
            "multiple": True,
            "typeClass": "compound",
            "value": [
              {
                "dateOfCollectionStart": {
                  "typeName": "dateOfCollectionStart",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "1006-01-01"
                },
                "dateOfCollectionEnd": {
                  "typeName": "dateOfCollectionEnd",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "1006-01-01"
                }
              },
              {
                "dateOfCollectionStart": {
                  "typeName": "dateOfCollectionStart",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "1006-02-01"
                },
                "dateOfCollectionEnd": {
                  "typeName": "dateOfCollectionEnd",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "1006-02-02"
                }
              }
            ]
          },
          {
            "typeName": "kindOfData",
            "multiple": True,
            "typeClass": "primitive",
            "value": [
              "KindOfData1",
              "KindOfData2"
            ]
          },
          {
            "typeName": "series",
            "multiple": True,
            "typeClass": "compound",
            "value": [
              {
                "seriesName": {
                  "typeName": "seriesName",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "SeriesName"
                },
                "seriesInformation": {
                  "typeName": "seriesInformation",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "SeriesInformation"
                }
              }
            ]
          },
          {
            "typeName": "software",
            "multiple": True,
            "typeClass": "compound",
            "value": [
              {
                "softwareName": {
                  "typeName": "softwareName",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "SoftwareName1"
                },
                "softwareVersion": {
                  "typeName": "softwareVersion",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "SoftwareVersion1"
                }
              },
              {
                "softwareName": {
                  "typeName": "softwareName",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "SoftwareName2"
                },
                "softwareVersion": {
                  "typeName": "softwareVersion",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "SoftwareVersion2"
                }
              }
            ]
          },
          {
            "typeName": "relatedMaterial",
            "multiple": True,
            "typeClass": "primitive",
            "value": [
              "RelatedMaterial1",
              "RelatedMaterial2"
            ]
          },
          {
            "typeName": "relatedDatasets",
            "multiple": True,
            "typeClass": "primitive",
            "value": [
              "RelatedDatasets1",
              "RelatedDatasets2"
            ]
          },
          {
            "typeName": "otherReferences",
            "multiple": True,
            "typeClass": "primitive",
            "value": [
              "OtherReferences1",
              "OtherReferences2"
            ]
          },
          {
            "typeName": "dataSources",
            "multiple": True,
            "typeClass": "primitive",
            "value": [
              "DataSources1",
              "DataSources2"
            ]
          },
          {
            "typeName": "originOfSources",
            "multiple": False,
            "typeClass": "primitive",
            "value": "OriginOfSources"
          },
          {
            "typeName": "characteristicOfSources",
            "multiple": False,
            "typeClass": "primitive",
            "value": "CharacteristicOfSourcesNoted"
          },
          {
            "typeName": "accessToSources",
            "multiple": False,
            "typeClass": "primitive",
            "value": "DocumentationAndAccessToSources"
          }
        ]
      },
      "geospatial": {
        "displayName": "Geospatial Metadata",
        "fields": [
          {
            "typeName": "geographicCoverage",
            "multiple": True,
            "typeClass": "compound",
            "value": [
              {
                "country": {
                  "typeName": "country",
                  "multiple": False,
                  "typeClass": "controlledVocabulary",
                  "value": "Afghanistan"
                },
                "state": {
                  "typeName": "state",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "GeographicCoverageStateProvince1"
                },
                "city": {
                  "typeName": "city",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "GeographicCoverageCity1"
                },
                "otherGeographicCoverage": {
                  "typeName": "otherGeographicCoverage",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "GeographicCoverageOther1"
                }
              },
              {
                "country": {
                  "typeName": "country",
                  "multiple": False,
                  "typeClass": "controlledVocabulary",
                  "value": "Albania"
                },
                "state": {
                  "typeName": "state",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "GeographicCoverageStateProvince2"
                },
                "city": {
                  "typeName": "city",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "GeographicCoverageCity2"
                },
                "otherGeographicCoverage": {
                  "typeName": "otherGeographicCoverage",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "GeographicCoverageOther2"
                }
              }
            ]
          },
          {
            "typeName": "geographicUnit",
            "multiple": True,
            "typeClass": "primitive",
            "value": [
              "GeographicUnit1",
              "GeographicUnit2"
            ]
          },
          {
            "typeName": "geographicBoundingBox",
            "multiple": True,
            "typeClass": "compound",
            "value": [
              {
                "westLongitude": {
                  "typeName": "westLongitude",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "-72"
                },
                "eastLongitude": {
                  "typeName": "eastLongitude",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "-70"
                },
                "northLongitude": {
                  "typeName": "northLongitude",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "43"
                },
                "southLongitude": {
                  "typeName": "southLongitude",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "42"
                }
              },
              {
                "westLongitude": {
                  "typeName": "westLongitude",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "-18"
                },
                "eastLongitude": {
                  "typeName": "eastLongitude",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "-13"
                },
                "northLongitude": {
                  "typeName": "northLongitude",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "29"
                },
                "southLongitude": {
                  "typeName": "southLongitude",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "28"
                }
              }
            ]
          }
        ]
      },
      "socialscience": {
        "displayName": "Social Science and Humanities Metadata",
        "fields": [
          {
            "typeName": "unitOfAnalysis",
            "multiple": True,
            "typeClass": "primitive",
            "value": [
              "UnitOfAnalysis1",
              "UnitOfAnalysis2"
            ]
          },
          {
            "typeName": "universe",
            "multiple": True,
            "typeClass": "primitive",
            "value": [
              "Universe1",
              "Universe2"
            ]
          },
          {
            "typeName": "timeMethod",
            "multiple": False,
            "typeClass": "primitive",
            "value": "TimeMethod"
          },
          {
            "typeName": "dataCollector",
            "multiple": False,
            "typeClass": "primitive",
            "value": "LastDataCollector1, FirstDataCollector1"
          },
          {
            "typeName": "collectorTraining",
            "multiple": False,
            "typeClass": "primitive",
            "value": "CollectorTraining"
          },
          {
            "typeName": "frequencyOfDataCollection",
            "multiple": False,
            "typeClass": "primitive",
            "value": "Frequency"
          },
          {
            "typeName": "samplingProcedure",
            "multiple": False,
            "typeClass": "primitive",
            "value": "SamplingProcedure"
          },
          {
            "typeName": "targetSampleSize",
            "multiple": False,
            "typeClass": "compound",
            "value": {
              "targetSampleActualSize": {
                "typeName": "targetSampleActualSize",
                "multiple": False,
                "typeClass": "primitive",
                "value": "100"
              },
              "targetSampleSizeFormula": {
                "typeName": "targetSampleSizeFormula",
                "multiple": False,
                "typeClass": "primitive",
                "value": "TargetSampleSizeFormula"
              }
            }
          },
          {
            "typeName": "deviationsFromSampleDesign",
            "multiple": False,
            "typeClass": "primitive",
            "value": "MajorDeviationsForSampleDesign"
          },
          {
            "typeName": "collectionMode",
            "multiple": True,
            "typeClass": "primitive",
            "value": [
              "CollectionMode"
            ]
          },
          {
            "typeName": "researchInstrument",
            "multiple": False,
            "typeClass": "primitive",
            "value": "TypeOfResearchInstrument"
          },
          {
            "typeName": "dataCollectionSituation",
            "multiple": False,
            "typeClass": "primitive",
            "value": "CharacteristicsOfDataCollectionSituation"
          },
          {
            "typeName": "actionsToMinimizeLoss",
            "multiple": False,
            "typeClass": "primitive",
            "value": "ActionsToMinimizeLosses"
          },
          {
            "typeName": "controlOperations",
            "multiple": False,
            "typeClass": "primitive",
            "value": "ControlOperations"
          },
          {
            "typeName": "weighting",
            "multiple": False,
            "typeClass": "primitive",
            "value": "Weighting"
          },
          {
            "typeName": "cleaningOperations",
            "multiple": False,
            "typeClass": "primitive",
            "value": "CleaningOperations"
          },
          {
            "typeName": "datasetLevelErrorNotes",
            "multiple": False,
            "typeClass": "primitive",
            "value": "StudyLevelErrorNotes"
          },
          {
            "typeName": "responseRate",
            "multiple": False,
            "typeClass": "primitive",
            "value": "ResponseRate"
          },
          {
            "typeName": "samplingErrorEstimates",
            "multiple": False,
            "typeClass": "primitive",
            "value": "EstimatesOfSamplingError"
          },
          {
            "typeName": "otherDataAppraisal",
            "multiple": False,
            "typeClass": "primitive",
            "value": "OtherFormsOfDataAppraisal"
          },
          {
            "typeName": "socialScienceNotes",
            "multiple": False,
            "typeClass": "compound",
            "value": {
              "socialScienceNotesType": {
                "typeName": "socialScienceNotesType",
                "multiple": False,
                "typeClass": "primitive",
                "value": "NotesType"
              },
              "socialScienceNotesSubject": {
                "typeName": "socialScienceNotesSubject",
                "multiple": False,
                "typeClass": "primitive",
                "value": "NotesSubject"
              },
              "socialScienceNotesText": {
                "typeName": "socialScienceNotesText",
                "multiple": False,
                "typeClass": "primitive",
                "value": "NotesText"
              }
            }
          }
        ]
      },
      "astrophysics": {
        "displayName": "Astronomy and Astrophysics Metadata",
        "fields": [
          {
            "typeName": "astroType",
            "multiple": True,
            "typeClass": "controlledVocabulary",
            "value": [
              "Image",
              "Mosaic",
              "EventList",
              "Cube"
            ]
          },
          {
            "typeName": "astroFacility",
            "multiple": True,
            "typeClass": "primitive",
            "value": [
              "Facility1",
              "Facility2"
            ]
          },
          {
            "typeName": "astroInstrument",
            "multiple": True,
            "typeClass": "primitive",
            "value": [
              "Instrument1",
              "Instrument2"
            ]
          },
          {
            "typeName": "astroObject",
            "multiple": True,
            "typeClass": "primitive",
            "value": [
              "Object1",
              "Object2"
            ]
          },
          {
            "typeName": "resolution.Spatial",
            "multiple": False,
            "typeClass": "primitive",
            "value": "SpatialResolution"
          },
          {
            "typeName": "resolution.Spectral",
            "multiple": False,
            "typeClass": "primitive",
            "value": "SpectralResolution"
          },
          {
            "typeName": "resolution.Temporal",
            "multiple": False,
            "typeClass": "primitive",
            "value": "TimeResolution"
          },
          {
            "typeName": "coverage.Spectral.Bandpass",
            "multiple": True,
            "typeClass": "primitive",
            "value": [
              "Bandpass1",
              "Bandpass2"
            ]
          },
          {
            "typeName": "coverage.Spectral.CentralWavelength",
            "multiple": True,
            "typeClass": "primitive",
            "value": [
              "3001",
              "3002"
            ]
          },
          {
            "typeName": "coverage.Spectral.Wavelength",
            "multiple": True,
            "typeClass": "compound",
            "value": [
              {
                "coverage.Spectral.MinimumWavelength": {
                  "typeName": "coverage.Spectral.MinimumWavelength",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "4001"
                },
                "coverage.Spectral.MaximumWavelength": {
                  "typeName": "coverage.Spectral.MaximumWavelength",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "4002"
                }
              },
              {
                "coverage.Spectral.MinimumWavelength": {
                  "typeName": "coverage.Spectral.MinimumWavelength",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "4003"
                },
                "coverage.Spectral.MaximumWavelength": {
                  "typeName": "coverage.Spectral.MaximumWavelength",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "4004"
                }
              }
            ]
          },
          {
            "typeName": "coverage.Temporal",
            "multiple": True,
            "typeClass": "compound",
            "value": [
              {
                "coverage.Temporal.StartTime": {
                  "typeName": "coverage.Temporal.StartTime",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "1007-01-01"
                },
                "coverage.Temporal.StopTime": {
                  "typeName": "coverage.Temporal.StopTime",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "1007-01-02"
                }
              },
              {
                "coverage.Temporal.StartTime": {
                  "typeName": "coverage.Temporal.StartTime",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "1007-02-01"
                },
                "coverage.Temporal.StopTime": {
                  "typeName": "coverage.Temporal.StopTime",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "1007-02-02"
                }
              }
            ]
          },
          {
            "typeName": "coverage.Spatial",
            "multiple": True,
            "typeClass": "primitive",
            "value": [
              "SkyCoverage1",
              "SkyCoverage2"
            ]
          },
          {
            "typeName": "coverage.Depth",
            "multiple": False,
            "typeClass": "primitive",
            "value": "200"
          },
          {
            "typeName": "coverage.ObjectDensity",
            "multiple": False,
            "typeClass": "primitive",
            "value": "300"
          },
          {
            "typeName": "coverage.ObjectCount",
            "multiple": False,
            "typeClass": "primitive",
            "value": "400"
          },
          {
            "typeName": "coverage.SkyFraction",
            "multiple": False,
            "typeClass": "primitive",
            "value": "500"
          },
          {
            "typeName": "coverage.Polarization",
            "multiple": False,
            "typeClass": "primitive",
            "value": "Polarization"
          },
          {
            "typeName": "redshiftType",
            "multiple": False,
            "typeClass": "primitive",
            "value": "RedshiftType"
          },
          {
            "typeName": "resolution.Redshift",
            "multiple": False,
            "typeClass": "primitive",
            "value": "600"
          },
          {
            "typeName": "coverage.RedshiftValue",
            "multiple": True,
            "typeClass": "compound",
            "value": [
              {
                "coverage.Redshift.MinimumValue": {
                  "typeName": "coverage.Redshift.MinimumValue",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "701"
                },
                "coverage.Redshift.MaximumValue": {
                  "typeName": "coverage.Redshift.MaximumValue",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "702"
                }
              },
              {
                "coverage.Redshift.MinimumValue": {
                  "typeName": "coverage.Redshift.MinimumValue",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "703"
                },
                "coverage.Redshift.MaximumValue": {
                  "typeName": "coverage.Redshift.MaximumValue",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "704"
                }
              }
            ]
          }
        ]
      },
      "biomedical": {
        "displayName": "Life Sciences Metadata",
        "fields": [
          {
            "typeName": "studyDesignType",
            "multiple": True,
            "typeClass": "controlledVocabulary",
            "value": [
              "Case Control",
              "Cross Sectional",
              "Cohort Study",
              "Not Specified"
            ]
          },
          {
            "typeName": "studyFactorType",
            "multiple": True,
            "typeClass": "controlledVocabulary",
            "value": [
              "Age",
              "Biomarkers",
              "Cell Surface Markers",
              "Developmental Stage"
            ]
          },
          {
            "typeName": "studyAssayOrganism",
            "multiple": True,
            "typeClass": "controlledVocabulary",
            "value": [
              "Arabidopsis thaliana",
              "Bos taurus",
              "Caenorhabditis elegans",
              "Danio rerio (zebrafish)"
            ]
          },
          {
            "typeName": "studyAssayOtherOrganism",
            "multiple": True,
            "typeClass": "primitive",
            "value": [
              "OtherOrganism1",
              "OtherOrganism2"
            ]
          },
          {
            "typeName": "studyAssayMeasurementType",
            "multiple": True,
            "typeClass": "controlledVocabulary",
            "value": [
              "genome sequencing",
              "cell sorting",
              "clinical chemistry analysis",
              "DNA methylation profiling"
            ]
          },
          {
            "typeName": "studyAssayOtherMeasurmentType",
            "multiple": True,
            "typeClass": "primitive",
            "value": [
              "OtherMeasurementType1",
              "OtherMeasurementType2"
            ]
          },
          {
            "typeName": "studyAssayTechnologyType",
            "multiple": True,
            "typeClass": "controlledVocabulary",
            "value": [
              "culture based drug susceptibility testing, single concentration",
              "culture based drug susceptibility testing, two concentrations",
              "culture based drug susceptibility testing, three or more concentrations (minimum inhibitory concentration measurement)",
              "flow cytometry"
            ]
          },
          {
            "typeName": "studyAssayPlatform",
            "multiple": True,
            "typeClass": "controlledVocabulary",
            "value": [
              "210-MS GC Ion Trap (Varian)",
              "220-MS GC Ion Trap (Varian)",
              "225-MS GC Ion Trap (Varian)",
              "300-MS quadrupole GC/MS (Varian)"
            ]
          },
          {
            "typeName": "studyAssayCellType",
            "multiple": True,
            "typeClass": "primitive",
            "value": [
              "CellType1",
              "CellType2"
            ]
          }
        ]
      },
      "journal": {
        "displayName": "Journal Metadata",
        "fields": [
          {
            "typeName": "journalVolumeIssue",
            "multiple": True,
            "typeClass": "compound",
            "value": [
              {
                "journalVolume": {
                  "typeName": "journalVolume",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "JournalVolume1"
                },
                "journalIssue": {
                  "typeName": "journalIssue",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "JournalIssue1"
                },
                "journalPubDate": {
                  "typeName": "journalPubDate",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "1008-01-01"
                }
              },
              {
                "journalVolume": {
                  "typeName": "journalVolume",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "JournalVolume2"
                },
                "journalIssue": {
                  "typeName": "journalIssue",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "JournalIssue2"
                },
                "journalPubDate": {
                  "typeName": "journalPubDate",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": "1008-02-01"
                }
              }
            ]
          },
          {
            "typeName": "journalArticleType",
            "multiple": False,
            "typeClass": "controlledVocabulary",
            "value": "abstract"
          }
        ]
      }
    }
  }
}
