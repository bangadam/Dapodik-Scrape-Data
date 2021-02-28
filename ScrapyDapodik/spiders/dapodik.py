from urllib.parse import urljoin
import scrapy
import pprint

class DapodikSpider(scrapy.Spider):
    name = 'dapodik'
    allowed_domains = ['referensi.data.kemdikbud.go.id']
    # start_urls = ['https://referensi.data.kemdikbud.go.id']

    def start_requests(self):
        return [scrapy.FormRequest("https://referensi.data.kemdikbud.go.id/index11.php",
                                   callback=self.parseProvinces)]

    def parseProvinces(self, response):
        parent = response.xpath('//div[@id="content"]')
        table = parent.xpath('.//table[@id="box-table-a"]')
        provinces = table.xpath('.//tbody/tr')
        del provinces[0]
        for province in provinces:
            provinceName = province.xpath('.//td[2]/a/text()').get()
            provinceUrl = province.xpath('.//td[2]/a/@href').get()
            districtUrl = response.urljoin(provinceUrl)
            yield scrapy.Request(url=districtUrl, callback=self.parseDistricts, meta={'provinceName': provinceName})

    def parseDistricts(self, response):
        parent = response.xpath('//div[@id="content"]')
        table = parent.xpath('.//table[@id="box-table-a"]')
        districts = table.xpath('.//tbody/tr')
        del districts[0]
        for district in districts:
            districtName = districts.xpath('.//td[2]/a/text()').get()
            districtUrl = districts.xpath('.//td[2]/a/@href').get()
            
            districtUrl = response.urljoin(districtUrl)
            yield scrapy.Request(url=districtUrl, callback=self.parseSubDistricts, meta={
                "provinceName": response.meta['provinceName'],
                "districtName": districtName
            })

    def parseSubDistricts(self, response):
        parent = response.xpath('//div[@id="content"]')
        table = parent.xpath('.//table[@id="box-table-a"]')
        subDistricts = table.xpath('.//tbody/tr')
        del subDistricts[0]
        for subDistrict in subDistricts:
            subDistrictName = subDistrict.xpath('.//td[2]/a/text()').get()
            subDistrictUrl = subDistrict.xpath('.//td[2]/a/@href').get()
            
            subDistrictUrl = response.urljoin(subDistrictUrl)
            
            yield scrapy.Request(url=subDistrictUrl, callback=self.parseEducation, meta={
                "provinceName": response.meta['provinceName'],
                "districtName": response.meta['districtName'],
                "subDistrictName": subDistrictName
            })

    def parseEducation(self, response):
        educations = response.xpath('//table[(@id = "example")]//tr')
        for education in educations:
            educationUrl = education.xpath('.//td[2]/a/@href').get()
            educationUrl = response.urljoin(educationUrl)
            
            yield scrapy.Request(url=educationUrl, callback=self.parseEducationDetail, meta={
                "provinceName": response.meta['provinceName'],
                "districtName": response.meta['districtName'],
                "subDistrictName": response.meta['subDistrictName']
            })

    def parseEducationDetail(self, response):
        tabOne = response.xpath('//div[@id="tabs-1"]')
        tabTwo = response.xpath('//div[@id="tabs-2"]')
        tabThree = response.xpath('//div[@id="tabs-3"]')

        tableOne = tabOne.xpath('.//td[@valign="top"]/table')
        tableTwo = tabTwo.xpath('.//table[2]')
        tableThree = tabThree.xpath('.//table[1]')

        # IDENTITAS SEKOLAH
        schoolName              = tableOne.xpath('.//tr[1]/td[4]/a/text()').get()
        schoolNPSN              = tableOne.xpath('.//tr[2]/td[4]/text()').get()
        schoolAddress           = tableOne.xpath('.//tr[3]/td[4]/text()').get()
        schoolZipCode           = tableOne.xpath('.//tr[4]/td[4]/text()').get()
        schoolVillages          = tableOne.xpath('.//tr[5]/td[4]/text()').get()
        schoolSubDistricts      = tableOne.xpath('.//tr[6]/td[4]/text()').get()
        schoolDistricts         = tableOne.xpath('.//tr[7]/td[4]/text()').get()
        schoolProvinces         = tableOne.xpath('.//tr[8]/td[4]/text()').get()
        schoolStatus            = tableOne.xpath('.//tr[9]/td[4]/text()').get()
        schoolOperationDate     = tableOne.xpath('.//tr[12]/td[4]/text()').get()
        schoolEducationalStage  = tableOne.xpath('.//tr[14]/td[4]/text()').get()

        # DOKUMEN & PERJANJIAN SEKOLAH
        schoolNaungan           = tableTwo.xpath('.//tr[1]/td[4]/text()').get()
        schoolNoSKPendirian     = tableTwo.xpath('.//tr[2]/td[4]/text()').get()
        schoolDateSKPendirian   = tableTwo.xpath('.//tr[3]/td[4]/text()').get()
        schoolNoSKOperasional   = tableTwo.xpath('.//tr[5]/td[4]/text()').get()
        schoolDateSKOperasional   = tableTwo.xpath('.//tr[6]/td[4]/text()').get()
        schoolFileSKOperasional   = tableTwo.xpath('.//tr[7]/td[4]/text()').get()
        schoollAkreditasi   = tableTwo.xpath('.//tr[9]/td[4]/strong/text()').get()
        schoolNoSKAkreditasi   = tableTwo.xpath('.//tr[11]/td[4]/text()').get()
        schoolDateSKAkreditasi   = tableTwo.xpath('.//tr[12]/td[4]/text()').get()
        schoolNoSertifikasiISO   = tableTwo.xpath('.//tr[14]/td[4]/text()').get()

        # SARANA PRASARANA SEKOLAH
        schoolLuasTanah = tableThree.xpath('.//tr[1]/td[4]/text()').get().replace("\u00a0m", ' m2')
        schoolAksesInternet = tableThree.xpath('.//tr[2]/td[4]/text()').get()
        schoolSumberListrik = tableThree.xpath('.//tr[4]/td[4]/text()').get()

        
        yield {
            "provinsi": response.meta['provinceName'],
            "kabupatenKota": response.meta['districtName'],
            "kecamatan": response.meta['subDistrictName'],
            "sekolahNama": schoolName,
            "sekolahNPSN": schoolNPSN,
            "sekolahAlamat": schoolAddress,
            "sekolahKodePos": schoolZipCode,
            "sekolahKelurahan": schoolVillages,
            "sekolahKecamatan": schoolSubDistricts,
            "sekolahKabupaten": schoolDistricts,
            "sekolahProvinsi": schoolProvinces,
            "sekolahStatus": schoolStatus,
            "sekolahTanggalOperasi": schoolOperationDate,
            "sekolahJenjangPendidikan": schoolEducationalStage,
            "sekolahNaungan": schoolNaungan,
            "sekolahNoSKPendirian": schoolNoSKPendirian,
            "sekolahTanggalSKPendirian": schoolDateSKPendirian,
            "sekolahNoSKOperasional": schoolNoSKOperasional,
            "sekolahTanggalSKOperasional": schoolDateSKOperasional,
            "sekolahBerkasSKOperasional": schoolFileSKOperasional,
            "sekolahlAkreditasi": schoollAkreditasi,
            "sekolahNoSKAkreditasi": schoolNoSKAkreditasi,
            "sekolahDateSKAkreditasi": schoolDateSKAkreditasi,
            "sekolahNoSertifikasiISO": schoolNoSertifikasiISO,
            "sekolahLuasTanah": schoolLuasTanah,
            "sekolahAksesInternet": schoolAksesInternet,
            "sekolahSumberListrik": schoolSumberListrik,
        }
        

