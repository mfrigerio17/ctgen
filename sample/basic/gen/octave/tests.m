mc = CtgenSampleModelConstants;

tf = frameA_xh_frameB(mc);
ds = BinDataset('dataset_frameA_X_frameB.bin');
display("Testing matrix frameA_X_frameB . . .");
ds.testMatrix(tf, 0, 0);
display("");

tf = frameD_xh_frameB(mc);
ds = BinDataset('dataset_frameD_X_frameB.bin');
display("Testing matrix frameD_X_frameB . . .");
ds.testMatrix(tf, 0, 2);
display("");

tf = frameE_xh_frameG(mc);
ds = BinDataset('dataset_frameE_X_frameG.bin');
display("Testing matrix frameE_X_frameG . . .");
ds.testMatrix(tf, 3, 0);
display("");

