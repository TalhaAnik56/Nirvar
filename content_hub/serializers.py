from rest_framework import serializers

from core.models import User

from .models import (
    Answer,
    Article,
    Like,
    Personal_Story,
    PersonalStoryImage,
    Question,
    RecommendedByDoctor,
    SymptomsDiary,
    Testimonial,
)


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = [
            "id",
            "user",
            "content",
            "raw_content",
            "created_at",
        ]

    user = SimpleUserSerializer(read_only=True)
    content = serializers.CharField(read_only=True)
    raw_content = serializers.CharField(write_only=True)
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)

    def save(self, **kwargs):
        user = self.context["user"]
        self.instance = Testimonial.objects.create(**self.validated_data, user=user)
        return self.instance


class UpdateTestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ["raw_content"]

    def save(self, **kwargs):
        testimonial = self.instance
        user = self.context["user"]

        if testimonial.user.id == user.id:
            testimonial.raw_content = self.validated_data["raw_content"]
            testimonial.save()
            self.instance = testimonial
            return self.instance
        else:
            raise serializers.ValidationError(
                {
                    "error": "This is not your testimonial. You can't update or delete this"
                }
            )


class PersonalStoryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalStoryImage
        fields = ["id", "image"]

    def create(self, validated_data):
        personal_story_id = self.context["personal_story_id"]
        personal_story = Personal_Story.objects.get(id=personal_story_id)
        return PersonalStoryImage.objects.create(
            personal_story=personal_story, **validated_data
        )


class PersonalStorySerializer(serializers.ModelSerializer):
    images = PersonalStoryImageSerializer(many=True, read_only=True)

    class Meta:
        model = Personal_Story
        fields = [
            "id",
            "user",
            "title",
            "content",
            "raw_content",
            "images",
            "created_at",
        ]

    user = SimpleUserSerializer(read_only=True)
    content = serializers.CharField(read_only=True)
    raw_content = serializers.CharField(write_only=True)
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)

    def save(self, **kwargs):
        user = self.context["user"]
        self.instance = Personal_Story.objects.create(**self.validated_data, user=user)
        return self.instance


class UpdatePersonalStorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Personal_Story
        fields = ["title", "raw_content"]

    def save(self, **kwargs):
        testimonial = self.instance
        user = self.context["user"]

        if testimonial.user.id == user.id:
            testimonial.title = self.validated_data["title"]
            testimonial.raw_content = self.validated_data["raw_content"]
            testimonial.save()
            self.instance = testimonial
            return self.instance
        else:
            raise serializers.ValidationError(
                {"error": "This is not your story. You can't update or delete this"}
            )


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "user", "image", "content", "answer_count", "created_at"]

    user = SimpleUserSerializer(read_only=True)
    answer_count = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)

    def create(self, validated_data):
        user = self.context["user"]
        return Question.objects.create(user=user, **validated_data)


class UpdateQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "user", "image", "content", "answer_count", "created_at"]

    user = SimpleUserSerializer(read_only=True)
    answer_count = serializers.IntegerField(read_only=True)
    id = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)

    def save(self, **kwargs):
        question = self.instance
        question.content = self.validated_data["content"]

        if "image" in self.validated_data and self.validated_data["image"] is not None:
            question.image = self.validated_data["image"]

        question.save()
        self.instance = question
        return self.instance


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = [
            "id",
            "user",
            "question",
            "content",
            "verified",
            "like_count",
            "created_at",
        ]

    user = SimpleUserSerializer(read_only=True)
    question = serializers.PrimaryKeyRelatedField(read_only=True)
    verified = serializers.BooleanField(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)

    def create(self, validated_data):
        user = self.context["user"]
        question_id = self.context["question_id"]
        return Answer.objects.create(
            user=user, question_id=question_id, **validated_data
        )


class UpdateAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = [
            "id",
            "user",
            "question",
            "content",
            "verified",
            "like_count",
            "created_at",
        ]

    user = SimpleUserSerializer(read_only=True)
    question = serializers.PrimaryKeyRelatedField(read_only=True)
    verified = serializers.BooleanField(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)

    def save(self, **kwargs):
        answer = self.instance
        user = self.context["user"]
        if answer.user.id == user.id:
            answer.content = self.validated_data["content"]
            answer.save()
            self.instance = answer
            return self.instance
        else:
            raise serializers.ValidationError(
                "This is not your answer. You can't update it"
            )


class VerifyAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["verified"]

    def save(self, **kwargs):
        answer = self.instance
        if answer.verified == False:
            answer.verified = self.validated_data["verified"]
            answer.save()
            self.instance = answer
            return self.instance
        else:
            raise serializers.ValidationError(
                "This comment is verified, you can't change it"
            )


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ["id", "answer", "user"]

    answer = serializers.PrimaryKeyRelatedField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            "id",
            "user",
            "title",
            "content",
            "image",
            "target_audience",
            "minimum_age_required",
            "recommendation_count",
            "created_at",
        ]

    user = SimpleUserSerializer(read_only=True)
    recommendation_count = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)

    def create(self, validated_data):
        user = self.context["user"]
        article = Article.objects.create(user=user, **validated_data)
        return article


class UpdateArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            "id",
            "user",
            "title",
            "content",
            "image",
            "target_audience",
            "minimum_age_required",
            "recommendation_count",
            "created_at",
        ]

    user = SimpleUserSerializer(read_only=True)
    recommendation_count = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)

    def save(self, **kwargs):
        article = self.instance
        user = self.context["user"]
        if article.user.id == user.id:
            article.title = self.validated_data["title"]
            article.content = self.validated_data["content"]
            article.target_audience = self.validated_data["target_audience"]
            article.minimum_age_required = self.validated_data["minimum_age_required"]
            article.image = self.validated_data["image"]
            article.save()
            self.instance = article
            return self.instance
        else:
            raise serializers.ValidationError(
                "This is not your article. You can't update it"
            )


class RecommendArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendedByDoctor
        fields = ["id", "article", "user"]

    article = serializers.PrimaryKeyRelatedField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)


class SymptomsDiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = SymptomsDiary
        fields = [
            "id",
            "user",
            "start_date",
            "finish_date",
            "pain_intensity",
            "other_symptoms",
        ]

    user = SimpleUserSerializer(read_only=True)
    start_date = serializers.DateField(
        format="%d-%m-%Y", input_formats=["%d-%m-%Y", "%Y-%m-%d"]
    )

    finish_date = serializers.DateField(
        format="%d-%m-%Y", input_formats=["%d-%m-%Y", "%Y-%m-%d"]
    )

    def create(self, validated_data):
        user = self.context["user"]
        diary = SymptomsDiary.objects.create(user=user, **validated_data)
        return diary


class UpdateSymptomsDiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = SymptomsDiary
        fields = [
            "id",
            "user",
            "start_date",
            "finish_date",
            "pain_intensity",
            "other_symptoms",
        ]

    user = SimpleUserSerializer(read_only=True)
    start_date = serializers.DateField(
        format="%d-%m-%Y", input_formats=["%d-%m-%Y", "%Y-%m-%d"]
    )

    finish_date = serializers.DateField(
        format="%d-%m-%Y", input_formats=["%d-%m-%Y", "%Y-%m-%d"]
    )

    def save(self, **kwargs):
        diary = self.instance
        user = self.context["user"]
        if diary.user.id == user.id:
            diary.start_date = self.validated_data["start_date"]
            diary.finish_date = self.validated_data["finish_date"]
            diary.pain_intensity = self.validated_data["pain_intensity"]

            diary.other_symptoms = self.validated_data["other_symptoms"]
            diary.save()
            self.instance = diary
            return self.instance
        else:
            raise serializers.ValidationError(
                "This is not your record. You can't update it"
            )
