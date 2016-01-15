
from django.test import SimpleTestCase
from django.core import management
from FaraData.models import Client, Registrant, ClientReg, Historical, HistoricalDoc, MetaData, Location


class PlainDataMergeTestCase(SimpleTestCase):
    def setUp(self):
        Historical.objects.create(principal="Rachel",
            location_represented="Sunlight",
            registrant="Bob",
            registrant_no="123")
        hist = Historical.objects.all()[0]
        HistoricalDoc.objects.create(historical_relationship=hist,
            document_link="www.example.com")
        MetaData.objects.create(link="www.example.com")
        Location.objects.create(location="Sunlight")

    def test_data_merge_with_no_dupes(self):
        """merge_feeds is successful when no duplicates are present"""
        management.call_command('merge_feeds')
        self.assertEqual(Client.objects.count(),1)
        self.assertEqual(Registrant.objects.count(),1)
        self.assertEqual(ClientReg.objects.count(),1)

    def tearDown(self):
        Historical.objects.all().delete()
        HistoricalDoc.objects.all().delete()
        MetaData.objects.all().delete()
        Location.objects.all().delete()
        Client.objects.all().delete()
        Registrant.objects.all().delete()
        ClientReg.objects.all().delete()

class KnownRegMergeTestCase(SimpleTestCase):
    def setUp(self):
        Historical.objects.create(principal="Rachel",
            location_represented="Sunlight",
            registrant="Bob",
            registrant_no="123")
        hist = Historical.objects.all()[0]
        HistoricalDoc.objects.create(historical_relationship=hist,
            document_link="www.example.com")
        Registrant.objects.create(reg_id=123,
            reg_name="Bob")
        MetaData.objects.create(link="www.example.com")
        Location.objects.create(location="Sunlight")

    def test_data_merge_with_known_reg(self):
        """merge_feeds is successful when registrant already known"""
        management.call_command('merge_feeds')
        self.assertEqual(Client.objects.count(),1)
        self.assertEqual(Registrant.objects.count(),1)
        self.assertEqual(ClientReg.objects.count(),1)

    def tearDown(self):
        Historical.objects.all().delete()
        HistoricalDoc.objects.all().delete()
        MetaData.objects.all().delete()
        Location.objects.all().delete()
        Client.objects.all().delete()
        Registrant.objects.all().delete()
        ClientReg.objects.all().delete()

class KnownClientMergeTestCase(SimpleTestCase):
    def setUp(self):
        Historical.objects.create(principal="Rachel",
            location_represented="Sunlight",
            registrant="Bob",
            registrant_no="123")
        hist = Historical.objects.all()[0]
        HistoricalDoc.objects.create(historical_relationship=hist,
            document_link="www.example.com")
        sunlight = Location.objects.create(location="Sunlight")
        Client.objects.create(client_name="Rachel",
            location=sunlight)
        MetaData.objects.create(link="www.example.com")
        

    def test_data_merge_with_known_reg(self):
        """merge_feeds is successful when registrant already known"""
        management.call_command('merge_feeds')
        self.assertEqual(Client.objects.count(),1)
        self.assertEqual(Registrant.objects.count(),1)
        self.assertEqual(ClientReg.objects.count(),1)

    def tearDown(self):
        Historical.objects.all().delete()
        HistoricalDoc.objects.all().delete()
        MetaData.objects.all().delete()
        Location.objects.all().delete()
        Client.objects.all().delete()
        Registrant.objects.all().delete()
        ClientReg.objects.all().delete()


class UnrelatedClientMergeTestCase(SimpleTestCase):
    def setUp(self):
        Historical.objects.create(principal="Rachel",
            location_represented="Sunlight",
            registrant="Bob",
            registrant_no="123")
        hist = Historical.objects.all()[0]
        HistoricalDoc.objects.create(historical_relationship=hist,
            document_link="www.example.com")
        md = MetaData.objects.create(link="www.example.com")
        sunlight = Location.objects.create(location="Sunlight")
        client = Client.objects.create(client_name="Miles",
            location=sunlight)
        client.meta_data.add(md)
        client.save()
        
        

    def test_data_merge_unrelated_client(self):
        """merge_feeds does not add clients if any clients are found for metadata"""
        management.call_command('merge_feeds')
        self.assertEqual(Client.objects.count(),1)
        self.assertEqual(Registrant.objects.count(),1)
        self.assertEqual(ClientReg.objects.count(),1)

    def tearDown(self):
        Historical.objects.all().delete()
        HistoricalDoc.objects.all().delete()
        MetaData.objects.all().delete()
        Location.objects.all().delete()
        Client.objects.all().delete()
        Registrant.objects.all().delete()
        ClientReg.objects.all().delete()

class KnownClientMergeTestCase(SimpleTestCase):
    def setUp(self):
        Historical.objects.create(principal="Rachel",
            location_represented="Sunlight",
            registrant="Bob",
            registrant_no="123")
        hist = Historical.objects.all()[0]
        HistoricalDoc.objects.create(historical_relationship=hist,
            document_link="www.example.com")
        md = MetaData.objects.create(link="www.example.com")
        sunlight = Location.objects.create(location="Sunlight")
        client = Client.objects.create(client_name="Rachel",
            location=sunlight)
        client.save()
        
        

    def test_data_merge_unrelated_client(self):
        """merge_feeds does not add new clients if name matches existing client"""
        management.call_command('merge_feeds')
        self.assertEqual(Client.objects.count(),1)
        self.assertEqual(Registrant.objects.count(),1)
        self.assertEqual(ClientReg.objects.count(),1)

    def tearDown(self):
        Historical.objects.all().delete()
        HistoricalDoc.objects.all().delete()
        MetaData.objects.all().delete()
        Location.objects.all().delete()
        Client.objects.all().delete()
        Registrant.objects.all().delete()
        ClientReg.objects.all().delete()