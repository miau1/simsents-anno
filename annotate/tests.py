from django.test import TestCase
from django.test import Client
from annotate.models import *
from annotate.views import *

class LoginTestCase(TestCase):

        def setUp(self):
                User.objects.create_user(username = "first", password = "first")

        def test_login(self):
                c = Client()
                response = c.post("/login/", {"username": "first", "password": "first"}, follow = True)
                self.assertEquals(response.status_code, 200)

        def test_redirect_to_login_when_not_logged_in(self):
                self.assertEquals(True, True)

        def test_normal_user_can_access_pages(self):
                self.assertEquals(True, True)

        def test_superuser_can_access_pages(self):
                self.assertEquals(True, True)

class NextPairTestCase(TestCase):

        def setUp(self):
                u = User.objects.create_user(username = "first", password = "first")
                Annotator.objects.create(user = u, lang = "en")
                u = User.objects.create_user(username = "second", password = "second")
                Annotator.objects.create(user = u, lang = "en")
                u = User.objects.create_user(username = "third", password = "third")
                Annotator.objects.create(user = u, lang = "en")
                Sentencepair.objects.create(sentID = "1", sent1="oneone", sent2="onetwo", lang = "en")
                Sentencepair.objects.create(sentID = "2", sent1="twoone", sent2="twotwo", lang = "en")
                Sentencepair.objects.create(sentID = "3", sent1="threeone", sent2="threetwo", lang = "en")

        def test_sentencepairs_exist(self):
                s1 = Sentencepair.objects.get(sentID = "1")
                s2 = Sentencepair.objects.get(sentID = "2")
                s3 = Sentencepair.objects.get(sentID = "3")
                self.assertEquals(s1.sentID, "1")
                self.assertEquals(s2.sentID, "2")
                self.assertEquals(s3.sentID, "3")

        def test_nextPair_when_pair_has_no_annotations(self):
                u = User.objects.get(username="first")
                self.assertEquals(nextPair(u), Sentencepair.objects.get(sentID = "1").id)

        def test_nextPair_when_pair_has_one_annotation_not_by_current_user(self):
                u = User.objects.get(username = "first")
                u2 = User.objects.get(username = "second")
                s = Sentencepair.objects.get(sentID = "1")
                s2 = Sentencepair.objects.get(sentID = "2")
                showPair(u2, s)
                annotateLogic(s, 4, "second", "en")
                showPair(u2, s2)
                self.assertEquals(nextPair(u), Sentencepair.objects.get(sentID = "1").id)

        def test_nextPair_when_pair_has_one_annotation_by_current_user(self):
                u = User.objects.get(username = "first")
                s = Sentencepair.objects.get(sentID = "1")
                showPair(u, s)
                annotateLogic(s, 4, "first", "en")
                self.assertEquals(nextPair(u), Sentencepair.objects.get(sentID = "2").id)

        def test_nextPair_when_pair_has_two_annotations_but_none_by_current_user(self):
                u = User.objects.get(username = "first")
                u2 = User.objects.get(username = "second")
                u3 = User.objects.get(username = "third")
                s = Sentencepair.objects.get(sentID = "1")
                showPair(u2, s)
                annotateLogic(s, 4, "second", "en")
                showPair(u3, s)
                annotateLogic(s, 4, "third", "en")
                self.assertEquals(nextPair(u), Sentencepair.objects.get(sentID = "2").id)

        def test_nextPair_when_pair_has_two_annotations_and_one_by_current_user(self):
                u = User.objects.get(username = "first")
                u2 = User.objects.get(username = "second")
                s = Sentencepair.objects.get(sentID = "1")
                showPair(u, s)
                annotateLogic(s, 4, "first", "en")
                showPair(u2, s)
                annotateLogic(s, 4, "second", "en")
                self.assertEquals(nextPair(u), Sentencepair.objects.get(sentID = "2").id)

        def test_nextPair_when_only_single_annotations(self):
                u1 = User.objects.get(username = "first")
                u2 = User.objects.get(username = "second")
                s1 = Sentencepair.objects.get(sentID = "1")
                s2 = Sentencepair.objects.get(sentID = "2")
                s3 = Sentencepair.objects.get(sentID = "3")
                showPair(u1, s1)
                annotateLogic(s1, 4, "first", "en")
                self.assertEquals(nextPair(u1), Sentencepair.objects.get(sentID = "2").id)
                showPair(u1, s2)
                annotateLogic(s2, 4, "first", "en")
                self.assertEquals(nextPair(u1), Sentencepair.objects.get(sentID = "3").id)
                showPair(u1, s3)
                annotateLogic(s3, 4, "first", "en")
                self.assertEquals(nextPair(u1), -1)
                self.assertEquals(nextPair(u2), Sentencepair.objects.get(sentID = "1").id)

        def test_nextPair_when_only_double_annotations(self):
                u1 = User.objects.get(username = "first")
                u2 = User.objects.get(username = "second")
                s1 = Sentencepair.objects.get(sentID = "1")
                s2 = Sentencepair.objects.get(sentID = "2")
                s3 = Sentencepair.objects.get(sentID = "3")
                showPair(u1, s1)
                annotateLogic(s1, 4, "first", "en")
                self.assertEquals(nextPair(u1), Sentencepair.objects.get(sentID = "2").id)
                showPair(u2, s1)
                annotateLogic(s1, 4, "second", "en")
                self.assertEquals(nextPair(u2), Sentencepair.objects.get(sentID = "2").id)
                showPair(u1, s2)
                annotateLogic(s2, 4, "first", "en")
                self.assertEquals(nextPair(u1), Sentencepair.objects.get(sentID = "3").id)
                showPair(u2, s2)
                annotateLogic(s2, 4, "second", "en")
                self.assertEquals(nextPair(u2), Sentencepair.objects.get(sentID = "3").id)
                showPair(u1, s3)
                annotateLogic(s3, 4, "first", "en")
                self.assertEquals(nextPair(u1), -1)
                showPair(u1, s3)
                annotateLogic(s3, 4, "second", "en")
                self.assertEquals(nextPair(u2), -1)

        def test_nextPair_when_double_then_single_then_zero(self):
                u1 = User.objects.get(username = "first")
                u2 = User.objects.get(username = "second")
                s1 = Sentencepair.objects.get(sentID = "1")
                s2 = Sentencepair.objects.get(sentID = "2")
                s3 = Sentencepair.objects.get(sentID = "3")
                showPair(u1, s1)
                annotateLogic(s1, 4, "first", "en")
                self.assertEquals(nextPair(u1), Sentencepair.objects.get(sentID = "2").id)
                showPair(u2, s1)
                annotateLogic(s1, 4, "second", "en")
                self.assertEquals(nextPair(u2), Sentencepair.objects.get(sentID = "2").id)
                showPair(u1, s2)
                annotateLogic(s2, 4, "first", "en")
                self.assertEquals(nextPair(u1), Sentencepair.objects.get(sentID = "3").id)

        def test_nextPair_when_single_then_double_then_zero(self):
                u1 = User.objects.get(username = "first")
                u2 = User.objects.get(username = "second")
                s1 = Sentencepair.objects.get(sentID = "1")
                s2 = Sentencepair.objects.get(sentID = "2")
                s3 = Sentencepair.objects.get(sentID = "3")
                showPair(u1, s1)
                annotateLogic(s1, 4, "first", "en")
                self.assertEquals(nextPair(u1), Sentencepair.objects.get(sentID = "2").id)
                showPair(u1, s2)
                annotateLogic(s2, 4, "first", "en")
                self.assertEquals(nextPair(u1), Sentencepair.objects.get(sentID = "3").id)
                showPair(u2, s2)
                annotateLogic(s2, 4, "second", "en")
                self.assertEquals(nextPair(u2), Sentencepair.objects.get(sentID = "1").id)

        def test_nextPair_when_single_then_double_then_single(self):
                u1 = User.objects.get(username = "first")
                u2 = User.objects.get(username = "second")
                s1 = Sentencepair.objects.get(sentID = "1")
                s2 = Sentencepair.objects.get(sentID = "2")
                s3 = Sentencepair.objects.get(sentID = "3")
                showPair(u1, s1)
                annotateLogic(s1, 4, "first", "en")
                self.assertEquals(nextPair(u1), Sentencepair.objects.get(sentID = "2").id)
                showPair(u1, s2)
                annotateLogic(s2, 4, "first", "en")
                self.assertEquals(nextPair(u1), Sentencepair.objects.get(sentID = "3").id)
                showPair(u2, s2)
                annotateLogic(s2, 4, "second", "en")
                self.assertEquals(nextPair(u2), Sentencepair.objects.get(sentID = "1").id)
                showPair(u1, s3)
                annotateLogic(s3, 4, "first", "en")
                self.assertEquals(nextPair(u1), -1)

        def test_overall_number(self):
                self.assertEquals(True, True)

class AnnotateLogicTestCase(TestCase):

        def setUp(self):
                Sentencepair.objects.create(sentID = "1", sent1="oneone", sent2="onetwo", lang = "en")

        def test_annotate_when_no_annotations(self):
                s = Sentencepair.objects.get(sentID = "1")
                self.assertEquals(len(s.annotation_set.all()), 0)
                annotateLogic(s, 4, "first", "en")
                self.assertEquals(len(s.annotation_set.all()), 1)

        def test_annotate_when_one_annotation_not_by_current_user(self):
                s = Sentencepair.objects.get(sentID = "1")
                self.assertEquals(len(s.annotation_set.all()), 0)
                annotateLogic(s, 4, "second", "en")
                self.assertEquals(len(s.annotation_set.all()), 1)
                self.assertEquals(s.annotation_set.all()[0].name, "second")
                annotateLogic(s, 4, "first", "en")
                self.assertEquals(len(s.annotation_set.all()), 2)
                self.assertEquals(s.annotation_set.all()[1].name, "first")

        def test_annotate_when_one_annotation_by_current_user(self):
                s = Sentencepair.objects.get(sentID = "1")
                self.assertEquals(len(s.annotation_set.all()), 0)
                annotateLogic(s, 4, "first", "en")
                self.assertEquals(len(s.annotation_set.all()), 1)
                self.assertEquals(s.annotation_set.all()[0].category, 4)
                annotateLogic(s, 3, "first", "en")
                self.assertEquals(len(s.annotation_set.all()), 1)
                self.assertEquals(s.annotation_set.all()[0].category, 3)

        def test_annotate_when_two_annotations_and_none_by_current_user(self):
                s = Sentencepair.objects.get(sentID = "1")
                annotateLogic(s, 4, "second", "en")
                annotateLogic(s, 4, "third", "en")
                annos = s.annotation_set.all()
                self.assertEquals(len(annos), 2)
                self.assertEquals(annos[0].name, "second")
                self.assertEquals(annos[1].name, "third")
                annotateLogic(s, 3, "first", "en")
                annos = s.annotation_set.all()
                self.assertEquals(len(annos), 2)
                self.assertEquals(annos[0].name, "second")
                self.assertEquals(annos[1].name, "third")

        def test_annotate_when_two_annotations_and_one_by_current_user(self):
                s = Sentencepair.objects.get(sentID = "1")
                annotateLogic(s, 4, "first", "en")
                annotateLogic(s, 4, "second", "en")
                annos = s.annotation_set.all()
                self.assertEquals(len(annos), 2)
                self.assertEquals(annos[0].name, "first")
                self.assertEquals(annos[0].category, 4)
                self.assertEquals(annos[1].name, "second")
                annotateLogic(s, 3, "first", "en")
                annos = s.annotation_set.all()
                self.assertEquals(len(annos), 2)
                self.assertEquals(annos[0].name, "second")
                self.assertEquals(annos[1].name, "first")
                self.assertEquals(annos[1].category, 3)

class ShowPairTestCase(TestCase):

        def setUp(self):
                u = User.objects.create_user(username = "first", password = "first")
                Annotator.objects.create(user = u, lang = "en")
                u = User.objects.create_user(username = "second", password = "second")
                Annotator.objects.create(user = u, lang = "en")
                u = User.objects.create_user(username = "third", password = "third")
                Annotator.objects.create(user = u, lang = "en")
                Sentencepair.objects.create(sentID = "1", sent1="oneone", sent2="onetwo", lang = "en")
                Sentencepair.objects.create(sentID = "2", sent1="twoone", sent2="twotwo", lang = "en")
                Sentencepair.objects.create(sentID = "3", sent1="threeone", sent2="threetwo", lang = "en")


        def test_show_when_pair_has_no_annotations_and_is_shown_to_two_people(self):
                u1 = User.objects.get(username = "first")
                u2 = User.objects.get(username = "second")
                u3 = User.objects.get(username = "third")
                s1 = Sentencepair.objects.get(sentID = "1")
                s2 = Sentencepair.objects.get(sentID = "2")

                showPair(u1, s1)
                showPair(u2, s1)

                self.assertEquals(nextPair(u3), s2.id)

        def test_show_when_pair_has_no_annotations_and_is_shown_to_one_person(self):
                u1 = User.objects.get(username = "first")
                u3 = User.objects.get(username = "third")
                s1 = Sentencepair.objects.get(sentID = "1")

                showPair(u1, s1)

                self.assertEquals(nextPair(u3), s1.id)

        def test_show_when_pair_has_one_annotation_and_is_shown_to_two_people(self):
                u1 = User.objects.get(username = "first")
                u2 = User.objects.get(username = "second")
                u3 = User.objects.get(username = "third")
                s1 = Sentencepair.objects.get(sentID = "1")
                s2 = Sentencepair.objects.get(sentID = "2")

                Annotation.objects.create(sentencepair = s1, category = 4, name = "fourth")
                showPair(u1, s1)
                showPair(u2, s1)

                self.assertEquals(nextPair(u3), s2.id)

        def test_show_when_pair_has_one_annotation_and_is_shown_to_one_person(self):
                u1 = User.objects.get(username = "first")
                u3 = User.objects.get(username = "third")
                s1 = Sentencepair.objects.get(sentID = "1")
                s2 = Sentencepair.objects.get(sentID = "2")

                Annotation.objects.create(sentencepair = s1, category = 4, name = "fourth")
                showPair(u1, s1)

                self.assertEquals(nextPair(u3), s2.id)

