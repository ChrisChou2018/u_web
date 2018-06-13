from django.db import models

# Create your models here.



class Brands(models.Model):
    '''
    品牌表
    '''
    brand_id                    = models.AutoField(db_column="brand_id", primary_key=True, verbose_name="品牌ID")
    cn_name                     = models.CharField(db_column="cn_name", verbose_name="品牌中文名", max_length=255)
    cn_name_abridge             = models.CharField(db_column="cn_name_abridge", null=True, verbose_name="品牌中文名缩写", max_length=255)
    en_name                     = models.CharField(db_column="en_name", null=True, verbose_name="品牌英文名", max_length=255)
    form_country                = models.CharField(db_column="form_country", null=True, verbose_name="所属国家", max_length=255)
    key_word                    = models.CharField(db_column="key_word", null=True, verbose_name="搜索关键字", max_length=255)
    brand_about                 = models.CharField(db_column="brand_about", null=True, verbose_name="品牌简介", max_length=255)
    brand_image                 = models.CharField(db_column="brand_image", null=True, verbose_name="品牌图片路径", max_length=255)


    class Meta:
        db_table = "app_brands"


class Items(models.Model):
    '''
    商品表
    '''
    item_id                     = models.AutoField(db_column="item_id", primary_key=True, verbose_name='商品ID')
    item_name                   = models.CharField(db_column="item_name", verbose_name='商品名称', max_length=255)
    item_info                   = models.CharField(db_column="item_info", null=True, verbose_name='商品信息', max_length=255)
    item_code                   = models.CharField(db_column="item_code", null=True, verbose_name="商品编码", max_length=255)
    item_barcode                = models.CharField(db_column="item_barcode", null=True, verbose_name="商品条码", max_length=255)
    price                       = models.FloatField(db_column="price", null=True, verbose_name="商品原价")
    current_price               = models.FloatField(db_column='current_price', null=True, verbose_name="商品现价")
    foreign_price               = models.FloatField(db_column='foreign_price', null=True, verbose_name="国外价格")
    comment_count               = models.IntegerField(db_column="comment_count", null=True, verbose_name="评论数量")
    hot_value                   = models.IntegerField(db_column="hot_value", null=True, verbose_name="热度值")
    buy_count                   = models.IntegerField(db_column="buy_count", null=True, verbose_name="被购买次数")
    key_word                    = models.CharField(db_column="key_word", null=True, verbose_name="搜索关键字", max_length=255)
    origin                      = models.CharField(db_column="origin", null=True,  verbose_name="生产地", max_length=255)
    shelf_life                  = models.CharField(db_column="shelf_life", null=True, verbose_name="保质期", max_length=255)
    capacity                    = models.CharField(db_column="capacity", null=True, verbose_name="容量", max_length=255)
    specifications_type_choices = (
        (0, '瓶'),
        (1, '包'),
        (2, '套'),
        (3, '片'),
        (4, '支'),
        (5, '袋'),
        (6, '对'),
        (7, '盒')
    )
    specifications_type_id      = models.SmallIntegerField(db_column="specifications_type_id", choices=specifications_type_choices, null=True, verbose_name="规格类型")
    categories_id               = models.BigIntegerField(db_column="categories_id", null=True, verbose_name="分类ID")
    brand_id                    = models.BigIntegerField(db_column="brand_id", null=True, verbose_name="品牌ID")
    for_people                  = models.CharField(db_column="for_people", null=True, verbose_name="适用人群", max_length=255)
    weight                      = models.CharField(db_column="weight", null=True, verbose_name="重量", max_length=255)
    create_person               = models.CharField(db_column="create_person", verbose_name="创建人", max_length=255)
    create_time                 = models.IntegerField(db_column="create_time", verbose_name="创建时间")
    update_person               = models.CharField(db_column="update_person", null=True, verbose_name="更新人", max_length=255)
    update_time                 = models.IntegerField(db_column="update_time", verbose_name="更新时间")
    status                      = models.CharField(db_column="status", verbose_name="状态", default="normal", max_length=255)
    
    
    class Meta:
        db_table = "app_items"


class ItemImages(models.Model):
    '''
    商品图片表
    '''
    image_id       = models.AutoField(db_column="image_id", primary_key=True, verbose_name="图片ID")
    item_id        = models.BigIntegerField(db_column="item_id", verbose_name="所属商品ID")
    type_choces    = (
        (0, "title"),
        (1, "thumbicon"),
        (2, "item_title"),
        (4, "item"),
    )
    image_type      = models.IntegerField(db_column="image_type", choices=type_choces, verbose_name="图片类型")
    image_path      = models.CharField(db_column="image_path", verbose_name="路径", max_length=255)
    file_size       = models.CharField(db_column="file_size", verbose_name="文件大小", max_length=255)
    resolution      = models.CharField(db_column="resolution", verbose_name="分辨率", max_length=255)
    file_type       = models.CharField(db_column="file_type", verbose_name="文件类型", max_length=255)
    status          = models.CharField(db_column="status", verbose_name="状态", max_length=255)
    

    class Meta:
        db_table = "app_item_images"


class ItemTags(models.Model):
    '''
    商品标签表
    '''
    tag_id          = models.AutoField(db_column="tag_id", verbose_name="标签ID", primary_key=True)
    tag_name        = models.CharField(db_column="tag_name", verbose_name="标签名", max_length=255)
    item_id         = models.BigIntegerField(db_column="item_id", verbose_name="所属商品ID")
    
    
    class Meta:
        db_table = "app_item_tags"


class Categories(models.Model):
    '''
    商品分类表
    '''
    categorie_id    = models.AutoField(db_column="categorie_id", verbose_name="分类ID", primary_key=True)
    categorie_name  = models.CharField(db_column="categorie_name", verbose_name="分类名", max_length=255)
    type_choices    = (
        (0, '功效专区'),
        (1, '基础护理'),
        (2, '个性彩妆'),
        (3, '营养保健')
    )
    categorie_type  = models.SmallIntegerField(db_column="categorie_type", choices=type_choices, null=True, verbose_name="类别")
    image_path      = models.CharField(db_column="image_path", null=True, verbose_name="缩略图路径", max_length=255)

    class Meta:
        db_table = "app_categories"


class ItemComments(models.Model):
    '''
    商品评论表
    '''
    comment_id      = models.AutoField(db_column="comment_id", verbose_name="评论ID", primary_key=True)
    member_id       = models.BigIntegerField(db_column="member_id", verbose_name="评论用户ID")
    item_id         = models.BigIntegerField(db_column="item_id", verbose_name="所属商品ID")
    comment_content = models.CharField(max_length=255, db_column="comment_content", verbose_name="评论内容")
    # reply_id        = models.BigIntegerField(db_column="reply_id", null=True, verbose_name="回复的评论ID")
    create_time     = models.IntegerField(db_column="create_time", verbose_name="创建时间")
    status          = models.CharField(db_column="status", verbose_name="状态", default="normal", max_length=255)


    class Meta:
        db_table = "app_item_comments"


class CommentImages(models.Model):
    '''
    评论图片表
    '''
    image_id        = models.AutoField(db_column="image_id", verbose_name="图片ID", primary_key=True)
    comment_id      = models.BigIntegerField(db_column="comment_id", verbose_name="所属评论ID")
    image_path      = models.CharField(db_column="image_path", verbose_name="路径", max_length=255)
    file_size       = models.CharField(db_column="file_size", verbose_name="文件大小", max_length=255)
    resolution      = models.CharField(db_column="resolution", verbose_name="分辨率", max_length=255)
    file_type       = models.CharField(db_column="file_type", verbose_name="文件类型", default='.jpg', max_length=255)
    status          = models.CharField(db_column="status", verbose_name="状态", default="normal", max_length=255)


    class Meta:
        db_table = "app_comment_images"