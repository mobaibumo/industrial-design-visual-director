# Product DNA
分别提取 geometry_features（轮廓、主要体块、相对长宽高）、components（组件数量、位置、连接）、cmf_features（材料、颜色、工艺、纹理）、visual_features（视角、构图、光线、背景）。每条为 id、attribute、value、source（资产 ID 列表）、confidence。

Confirmed：用户或可靠资料确认；Observed：图像可见；Inferred：推测；Unknown：未知且 value=null。观察数量应写“可见数量”，不能把遮挡件当作不存在。无标尺不写真实尺寸；透视比例不是工程尺寸；不可见背面不补造。光照引起的颜色变化与材质本色分开记录。

source_assets 每项含 id、path、role、source；role 通常 target、cmf、scene、cad、result。路径必须真实可访问，合成示例需明确标注。按属性确定来源权威：当前用户要求 > CAD/工程尺寸 > 已确认多视图 > 已确认主视图 > 普通参考 > 推测。CMF 指定参考只支配 CMF，场景图只支配场景。权威冲突写入 unknowns 并暂停依赖该属性的编辑，不能静默裁决。

顶层字段见 assets/product-dna.json。schema_version=1.0，revision 正整数；unknowns 为问题列表。无结果、无尺寸、无背面资料是合法未知。