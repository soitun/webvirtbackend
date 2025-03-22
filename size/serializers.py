from rest_framework import serializers

from .models import Size, DBMS


class SizeSerializer(serializers.ModelSerializer):
    available = serializers.BooleanField(source="is_active")
    price_hourly = serializers.DecimalField(source="price", max_digits=10, decimal_places=6)
    price_monthly = serializers.SerializerMethodField()
    disk = serializers.SerializerMethodField()
    memory = serializers.SerializerMethodField()
    regions = serializers.SerializerMethodField()
    transfer = serializers.SerializerMethodField()

    class Meta:
        model = Size
        fields = (
            "slug",
            "memory",
            "vcpu",
            "disk",
            "transfer",
            "description",
            "available",
            "price_hourly",
            "price_monthly",
            "regions",
        )

    def get_disk(self, obj):
        return obj.disk // 1073741824

    def get_memory(self, obj):
        return obj.memory // 1048576

    def get_transfer(self, obj):
        return obj.transfer / 1099511627776

    def get_price_monthly(self, obj):
        return int(round(obj.price * (30 * 24), 0))

    def get_regions(self, obj):
        return [region.slug for region in obj.regions.all()]


class DBMSSerializer(serializers.ModelSerializer):
    sizes = serializers.SerializerMethodField()
    available = serializers.BooleanField(source="is_active")

    class Meta:
        model = DBMS
        fields = (
            "slug",
            "name",
            "sizes",
            "engine",
            "version",
            "available",
            "description",
        )

    def get_sizes(self, obj):
        size_list = []
        for size in obj.sizes.all():
            size_list.append(size)
        return SizeSerializer(size_list, many=True).data
