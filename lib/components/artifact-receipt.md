# 实际目标文件回执

使用成熟工具生成非HTML目标后，需要保存版本身份和实际文件检查时采用。仅Python3.10+标准库，只读明确输入与实物，JSON输出到标准输出；不调用生成器、网络、发布或业务写入。

```sh
python3 scripts/artifact_receipt.py --artifact-root <实际成品目录> --input targets.json
```

targets.json为`{"schema":1,"files":[{"path":"cards/01.png","kind":"png"}]}`。path必须是目录内唯一相对路径，拒绝越界和软链接；kind支持png/jpeg/pptx/wav/mp4/html。输入上限2MiB，单文件上限256MiB。缺失、空文件、格式头不符、截断WAV或缺原生PPTX部件返回exit2与INPUT_ERROR；所有声明文件完成所列检查时exit0与ACTUAL_FILES_RECORDED。

输出包含输入和文件SHA-256、实际字节、支持的局部结构结果：PNG头中的尺寸、WAV帧与实测时长、PPTX原生幻灯片XML部件数量。PNG/JPEG/MP4仅核文件头或所列结构，不做完整解码；MP4时长明确未知，需实际媒体工具另测。PPTX的XML存在不证明关系完整、可打开或页面可编辑；必须用实际演示工具核对。HTML只读UTF-8，不算媒体实物。

presentationAcceptance始终NOT_PERFORMED。调用者负责渲染／播放、作者内容、语义、许可与真实接受，不能把exit0写为成品验收通过。组件不覆盖文件，保留原目标与版本；输出重定向只用于本次新的证据位置，不覆盖旧回执。

消费者：create/adapt仅在实际制作目标文件且需要身份回执时采用；只成文与HTML制作不强制运行。
