% 计算Trade in value added 计算方法。
%中国社会科学院经济研究所 倪红福 编写

clear all
S=48                 %这里输入投入产出表中的国家（区域）数据。
N=17                 %这里输入每个国家（区域）的行业数。

G=xlsread('2007global.xlsx','sheet2')    % 从excel中读取数据 819*961


AA=G([1:S*N], [1:S*N])                  %取中间投入矩阵816*816
VA=G([S*N+2], [1:S*N])                  % 取增加值
TI=G([S*N+3], [1:S*N])                  %取总投入
TTI=inv(diag(TI,0) )                    %总投入矩阵对角化,并取倒数。
A=AA*TTI                               %直接消耗系数矩阵
v=VA*TTI                            %增加值系数向量
I=eye(S*N)                          %单位矩阵,单位矩阵生成函数
I1=eye(N)                           %部门数的单位矩阵
B=I/(I-A)                          %求列奥列夫逆矩阵，这个矩阵是一个全局的逆矩阵。
% 以下主要怎样利用循环语句从大矩阵中取按国家分的矩阵。
%使用单元组的处理方法，MATLAB处理矩阵的一个优势。
%模型中一定要知道数字对应的国家和部门。

%利用循环语句进行赋值。
FB=cell(S,S)                            % 生成一个48*48的单元组。celldisp
for i=1:1:S,
    for j=1:1:S
FB{i,j}=B([(i-1)*N+1:i*N],[(j-1)*N+1:j*N]);  %提取分块矩阵，取B中的j对i国家的完全消耗系数矩阵。
    end
end                                     
%celldisp(FB, 'complete matrix')               %显示分块完全消耗系数矩阵


FV=cell(S,S)                               %对增加值率分块,增加值率矩阵变为对角矩阵(N*N)。
for i=1:1:S
    for j=1:1:S
        if j==i
        FV{i,i}=diag(v(1,[(i-1)*N+1:i*N]) )  
        else
            FV{i,j}=zeros(N,N)
        end
    end
end                                        %循环获取增加值率分块矩阵。
%celldisp(FV,'value added rate')            %显示增加值率分块矩阵。


%因为最终需求矩阵分为消费、投资和存货，每一国家（区域）对应3列。
Y=G([1:N*S],[N*S+1:(N*S+3*S)])             %提出最终需求矩阵。     
 FY=cell(S,S)                              %生成一个3*3的单元矩阵。celldisp               
 for i=1:1:S,
     for j=1:1:S
         FY{i,j}=Y([(i-1)*N+1:i*N],[(j-1)*3+1:j*3])*ones(3,1);   %由于提取后，最终需求矩阵的数据重新排列后，注意列的选取。 
     end
 end
% celldisp(FY,'final demand')                                     %循环语句计算最终需求分块矩阵，并显示。


%计算分行业双边国家增加值出口。
 VT=cell(S,S) 
 
  for i=1:1:S,
    for j=1:1:S 
        VT{i,j}=zeros(N,1)
       for t=1:1:S 
       VT{i,j}=VT{i,j}+FV{i,i}*FB{i,t}*FY{t,j}
       end
    end
  end
%输出CSV格式的数据结果 
 csvwrite('vtdata2007.csv',VT)
 
 
 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
 %%%%%%%%增加值出口和流出的结构分解%%%%%%%%%%%%%%%%%%%%%%%%%%
 %%%%%%%%中国区域的排序编号为7-14（8个区域）%%%%%%%%%%%%%%%%%%
 
 %%%%%%%%%%%%%计算中国区域中局部逆矩阵%%%%%%%%%%%%%%%%%%%%%%%%
 
 %利用循环语句进行赋值。
FA=cell(S,S)                            % 生成一个48*48的单元组。celldisp
for i=1:1:S,
    for j=1:1:S
FA{i,j}=A([(i-1)*N+1:i*N],[(j-1)*N+1:j*N]);  %提取分块矩阵，取B中的j对i国家的直接消耗系数矩阵。
    end
end                                     
%celldisp(FB, 'complete matrix')               %显示分块直接消耗系数矩阵

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

 Ad=zeros(S*N,S*N)
 for i=1:1:S 
     Ad([(i-1)*N+1:i*N],[(i-1)*N+1:i*N])=FA{i,i}
 end
 
 for i=7:1:14
     for j=7:1:14
         Ad([(i-1)*N+1:i*N],[(j-1)*N+1:j*N])=FA{i,j}
     end
 end
 
 Bd=I/(I-Ad)  
 
 
  %利用循环语句进行赋值。
FBd=cell(S,S)                            % 生成一个48*48的单元组。celldisp
for i=1:1:S,
    for j=1:1:S
FBd{i,j}=Bd([(i-1)*N+1:i*N],[(j-1)*N+1:j*N]);  %提取分块矩阵，取B中的j对i国家的局部逆系数矩阵。
    end
end                                     
%celldisp(FB, 'complete matrix')               %显示分块局部逆系数矩阵


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
 
 %%%%%计算第1项的值
 VAT=cell(S,13) 
  for i=7:1:14
         VAT{i,1}=0
       for j=7:1:14 
       VAT{i,1}=VAT{i,1}+ones(1,N)*FV{i,i}*FBd{i,i}*FY{i,j}
       end 
        VAT{i,1}=VAT{i,1}-ones(1,N)*FV{i,i}*FBd{i,i}*FY{i,i}
  end
    csvwrite('VAT2007.csv',VAT) 
   
   %%%%%计算第2项的值
   

  for i=7:1:14
         VAT{i,2}=-ones(1,N)*FV{i,i}*FBd{i,i}*FY{i,i}
       for j=7:1:14 
       VAT{i,2}=VAT{i,2}+ones(1,N)*FV{i,i}*FBd{i,j}*FY{j,j}
       end 
    end
    csvwrite('VAT2007.csv',VAT)   
 
     %%%%%计算第3项的值 
     for i=7:1:14
         VAT{i,3}=0
       for j=7:1:14 
           if j==i
              VAT{i,3}=VAT{i,3}
           else
               for t=7:1:14
                   if t==i | t==j
                    VAT{i,3}=VAT{i,3}
                   else
                     VAT{i,3}=VAT{i,3}+ones(1,N)*FV{i,i}*FBd{i,j}*FY{j,t}
                   end
               end
           end
       end 
    end
    csvwrite('VAT2007.csv',VAT)    
    
    %%%%%计算第4项%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
 
 for i=7:1:14
         VAT{i,4}=-ones(1,N)*FV{i,i}*(FB{i,i}-FBd{i,i})*FY{i,i}
       for j=7:1:14 
       VAT{i,4}=VAT{i,4}+ones(1,N)*FV{i,i}*(FB{i,i}-FBd{i,i})*FY{i,j}
       end 
    end
    csvwrite('VAT2007.csv',VAT) 
   
   %%%%%计算第5项的值

  for i=7:1:14
         VAT{i,5}=-ones(1,N)*FV{i,i}*(FB{i,i}-FBd{i,i})*FY{i,i}
       for j=7:1:14 
       VAT{i,5}=VAT{i,5}+ones(1,N)*FV{i,i}*(FB{i,j}-FBd{i,j})*FY{j,j}
       end 
    end
    csvwrite('VAT2007.csv',VAT)   
 
     %%%%%计算第6项的值 
     
     for i=7:1:14
         VAT{i,6}=0
       for j=7:1:14 
           if j==i
              VAT{i,6}=VAT{i,6}
           else
               for t=7:1:14
                   if t==i | t==j
                    VAT{i,6}=VAT{i,6}
                   else
                     VAT{i,6}=VAT{i,6}+ones(1,N)*FV{i,i}*(FB{i,j}-FBd{i,j})*FY{j,t}
                   end
               end
           end
       end 
    end
    csvwrite('VAT2007.csv',VAT)    

    %%%%%%%%%%%%%%%%%%%%%计算第7项%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
 
     VAT7_1=cell(S,1)
        
    for i=7:1:14
        VAT7_1{i,1}=0
      for j=1:1:6
          for t=7:1:14
             if t==i
            VAT7_1{i,1}= VAT7_1{i,1}
             else
             VAT7_1{i,1}=VAT7_1{i,1}+ ones(1,N)*FV{i,i}*FB{i,j}*FY{j,t}
             end
          end
      end
    end
  
    
     VAT7_2=cell(S,1)
     for i=7:1:14
       VAT7_2{i,1}=0
      for j=15:1:S
          for t=7:1:14
            if t==i
            VAT7_2{i,1}=VAT7_2{i,1}
            else
            VAT7_2{i,1}= VAT7_2{i,1}+ ones(1,N)*FV{i,i}*FB{i,j}*FY{j,t}
            end  
          end  
      end
     end
      
   for i=7:1:14
      VAT{i,7}=VAT7_1{i,1}+VAT7_2{i,1}
   end
  
    csvwrite('VAT2007.csv',VAT)   
    
    
    
    %%%%%%前7项是不存在问题%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    %%%%%%%%%%%%%%%%%%%%%计算第8项%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    %%%%%%%%%%%%%%%%%%%%%%%%%
    
    
    VAT8_1=cell(S,1)
        
    for i=7:1:14
        VAT8_1{i,1}=0
      for j=1:1:S
             VAT8_1{i,1}=VAT8_1{i,1}+ ones(1,N)*FV{i,i}*FB{i,j}*FY{j,j}    
      end
    end
    
     VAT8_2=cell(S,1)
     for i=7:1:14
       VAT8_2{i,1}=0
      for j=7:1:14
          VAT8_2{i,1}= VAT8_2{i,1}+ ones(1,N)*FV{i,i}*FB{i,j}*FY{j,j}
      end  
     end   
      
   for i=7:1:14
      VAT{i,8}=VAT8_1{i,1}-VAT8_2{i,1}
   end
  
    csvwrite('VAT2007.csv',VAT)   
   
   %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%第8项没问题%%%%%%%%%%
    
    
  
    %%%%%%%%%%%%%%%%%%%%%%%%计算第9项%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
      
    VAT9_1=cell(S,1)
        
    for i=7:1:14
        VAT9_1{i,1}=0
      for j=1:1:6
          for t=1:1:6
              if t==j
                VAT9_1{i,1}=VAT9_1{i,1}   
              else
             VAT9_1{i,1}=VAT9_1{i,1}+ ones(1,N)*FV{i,i}*FB{i,j}*FY{j,t} 
              end
          end
          for t=15:1:S
               VAT9_1{i,1}=VAT9_1{i,1}+ ones(1,N)*FV{i,i}*FB{i,j}*FY{j,t} 
          end
              
      end
    end
    
  
  VAT9_2=cell(S,1)
        
    for i=7:1:14
        VAT9_2{i,1}=0
      for j=15:1:S
          for t=1:1:6
             VAT9_2{i,1}=VAT9_2{i,1}+ ones(1,N)*FV{i,i}*FB{i,j}*FY{j,t} 
          end
          for t=15:1:S
               if t==j
                VAT9_2{i,1}=VAT9_2{i,1}   
              else
               VAT9_2{i,1}=VAT9_2{i,1}+ ones(1,N)*FV{i,i}*FB{i,j}*FY{j,t} 
               end
          end
              
      end
    end
      
   for i=7:1:14
      VAT{i,9}=VAT9_1{i,1}+VAT9_2{i,1}
   end
  
    csvwrite('VAT2007.csv',VAT)  
    
    %%%%%%%%%%%%%%%%%第9项没有问题%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    
    %%%%%%%%%%%%%计算第10项
    
    VAT10_1=cell(S,1)
    
    
    for i=7:1:14
        VAT10_1{i,1}=0
      for j=1:1:6
             VAT10_1{i,1}=VAT10_1{i,1}+ ones(1,N)*FV{i,i}*(FB{i,i}-FBd{i,i})*FY{i,j}    
      end
    end
    
     VAT10_2=cell(S,1)
     for i=7:1:14
       VAT10_2{i,1}=0
      for j=15:1:S
          VAT10_2{i,1}= VAT10_2{i,1}+ ones(1,N)*FV{i,i}*(FB{i,i}-FBd{i,i})*FY{i,j} 
       end  
     end
      
   for i=7:1:14
      VAT{i,10}=VAT10_1{i,1}+VAT10_2{i,1}
   end
  
    csvwrite('VAT2007.csv',VAT)   
    
   %%%%%%%%%%%%%%%%%%%%%%%%%%% 
   %%%%%%%第10项没问题%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
   
 
    %%%%%%%%%%%%%计算第11项
    
    VAT11_1=cell(S,1)
    
    for i=7:1:14
        VAT11_1{i,1}=0
        for j=7:1:14
            if j==i
               VAT11_1{i,1}=VAT11_1{i,1}
            else
          for t=1:1:6
             VAT11_1{i,1}=VAT11_1{i,1}+ ones(1,N)*FV{i,i}*(FB{i,j}-FBd{i,j})*FY{j,t} 
          end
            end
       end
    end 
    
     VAT11_2=cell(S,1)
     for i=7:1:14
       VAT11_2{i,1}=0
    for j=7:1:14
            if j==i
              VAT11_2{i,1}=VAT11_2{i,1}
            else
             for t=15:1:S      
              VAT11_2{i,1}= VAT11_2{i,1}+ ones(1,N)*FV{i,i}*(FB{i,j}-FBd{i,j})*FY{j,t} 
             end  
            end
    end
     end
     
      
   for i=7:1:14
      VAT{i,11}=VAT11_1{i,1}+VAT11_2{i,1}
   end
  
    csvwrite('VAT2007.csv',VAT)    
    
   %%%%%%%%%%%%%%%%%%第11项没问题%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
  
    %%%%%%%%%%%%%计算第12项
    
    VAT12_1=cell(S,1)
    
    for i=7:1:14
        VAT12_1{i,1}=0
      for j=1:1:6
             VAT12_1{i,1}=VAT12_1{i,1}+ ones(1,N)*FV{i,i}*FBd{i,i}*FY{i,j}    
      end
    end
    
     VAT12_2=cell(S,1)
     for i=7:1:14
       VAT12_2{i,1}=0
      for j=15:1:S
          VAT12_2{i,1}= VAT12_2{i,1}+ ones(1,N)*FV{i,i}*FBd{i,i}*FY{i,j} 
       end  
     end
      
   for i=7:1:14
      VAT{i,12}=VAT12_1{i,1}+VAT12_2{i,1}
   end
  
    csvwrite('VAT2007.csv',VAT)     
    
    
   %%%%%%%%%%%%%计算第13项
    
    VAT13_1=cell(S,1)
    
    for i=7:1:14
        VAT13_1{i,1}=0
        for j=7:1:14
            if j==i
               VAT13_1{i,1}=VAT13_1{i,1}
            else
          for t=1:1:6
             VAT13_1{i,1}=VAT13_1{i,1}+ ones(1,N)*FV{i,i}*FBd{i,j}*FY{j,t} 
          end
            end
       end
    end
    
     VAT13_2=cell(S,1)
     
     for i=7:1:14
       VAT13_2{i,1}=0
    for j=7:1:14
            if j==i
              VAT13_2{i,1}=VAT13_2{i,1}
            else
             for t=15:1:S      
          VAT13_2{i,1}= VAT13_2{i,1}+ ones(1,N)*FV{i,i}*FBd{i,j}*FY{j,t} 
             end  
            end
    end
     end
       
   for i=7:1:14
      VAT{i,13}=VAT13_1{i,1}+VAT13_2{i,1}
   end
  
    csvwrite('VAT2007.csv',VAT)    
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
      
       
    
      %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
   
      %%%%%%检查各区域增加值出口和流出%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
     VAXT=cell(S,1) 
  for i=7:1:14
         VAXT{i,1}=0
       for j=1:1:S
           for t=1:1:S
               if t==i
                  VAXT{i,1}=VAXT{i,1}
               else
            VAXT{i,1}=VAXT{i,1}+ones(1,N)*FV{i,i}*FB{i,j}*FY{j,t}
               end
           end
       end   
  end
    
 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%   
    
%%%%%%%%%%%%%%%%%不考虑纯的价值的分解%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

 %%%%%计算第1项的值
 AVAT=cell(S,13) 
  for i=7:1:14
         AVAT{i,1}=0
       for j=7:1:14 
       AVAT{i,1}=AVAT{i,1}+ones(1,N)*FV{i,i}*FB{i,i}*FY{i,j}
       end 
        AVAT{i,1}=AVAT{i,1}-ones(1,N)*FV{i,i}*FB{i,i}*FY{i,i}
  end
    csvwrite('AVATX2007.csv',AVAT) 
   
   %%%%%计算第2项的值
   

  for i=7:1:14
         AVAT{i,2}=-ones(1,N)*FV{i,i}*FB{i,i}*FY{i,i}
       for j=7:1:14 
       AVAT{i,2}=AVAT{i,2}+ones(1,N)*FV{i,i}*FB{i,j}*FY{j,j}
       end 
    end
    csvwrite('AVATX2007.csv',AVAT)   
 
     %%%%%计算第3项的值 
     for i=7:1:14
         AVAT{i,3}=0
       for j=7:1:14 
           if j==i
              AVAT{i,3}=AVAT{i,3}
           else
               for t=7:1:14
                   if t==i | t==j
                    AVAT{i,3}=AVAT{i,3}
                   else
                     AVAT{i,3}=AVAT{i,3}+ones(1,N)*FV{i,i}*FB{i,j}*FY{j,t}
                   end
               end
           end
       end 
    end
    csvwrite('AVATX2007.csv',AVAT)    
    
    
  
 
    
    %%%%%%%%%%%%%%%%%%%%%计算第7项%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
 
     AVAT7_1=cell(S,1)
        
    for i=7:1:14
        AVAT7_1{i,1}=0
      for j=1:1:6
          for t=7:1:14
             if t==i
            AVAT7_1{i,1}= AVAT7_1{i,1}
             else
             AVAT7_1{i,1}=AVAT7_1{i,1}+ ones(1,N)*FV{i,i}*FB{i,j}*FY{j,t}
             end
          end
      end
    end
  
    
     AVAT7_2=cell(S,1)
     for i=7:1:14
       AVAT7_2{i,1}=0
      for j=15:1:S
          for t=7:1:14
            if t==i
            AVAT7_2{i,1}=AVAT7_2{i,1}
            else
            AVAT7_2{i,1}= AVAT7_2{i,1}+ ones(1,N)*FV{i,i}*FB{i,j}*FY{j,t}
            end  
          end  
      end
     end
      
   for i=7:1:14
      AVAT{i,7}=AVAT7_1{i,1}+AVAT7_2{i,1}
   end
  
    csvwrite('AVATX2007.csv',AVAT)   
    
    %%%%%%%%%%%%%%%%%%%%%计算第8项%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    AVAT8_1=cell(S,1)
        
    for i=7:1:14
        AVAT8_1{i,1}=0
      for j=1:1:6
             AVAT8_1{i,1}=AVAT8_1{i,1}+ ones(1,N)*FV{i,i}*FB{i,j}*FY{j,j}    
      end
    end
    
     AVAT8_2=cell(S,1)
     for i=7:1:14
       AVAT8_2{i,1}=0
      for j=15:1:S
        
          AVAT8_2{i,1}= AVAT8_2{i,1}+ ones(1,N)*FV{i,i}*FB{i,j}*FY{j,j}
      end  
     end  
   
      
   for i=7:1:14
      AVAT{i,8}=AVAT8_1{i,1}+AVAT8_2{i,1}
   end
  
    csvwrite('AVATX2007.csv',AVAT)   
    
  
    %%%%%%%%%%%%%%%%%%%%%%%%计算第9项%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
      
    AVAT9_1=cell(S,1)
        
    for i=7:1:14
        AVAT9_1{i,1}=0
      for j=1:1:6
          for t=1:1:6
              if t==j
                AVAT9_1{i,1}=AVAT9_1{i,1}   
              else
             AVAT9_1{i,1}=AVAT9_1{i,1}+ ones(1,N)*FV{i,i}*FB{i,j}*FY{j,t} 
              end
          end
          for t=15:1:S
               AVAT9_1{i,1}=AVAT9_1{i,1}+ ones(1,N)*FV{i,i}*FB{i,j}*FY{j,t} 
          end
              
      end
    end
    
  
  AVAT9_2=cell(S,1)
        
    for i=7:1:14
        AVAT9_2{i,1}=0
      for j=15:1:S
          for t=1:1:6
             AVAT9_2{i,1}=AVAT9_2{i,1}+ ones(1,N)*FV{i,i}*FB{i,j}*FY{j,t} 
          end
          for t=15:1:S
               if t==j
                AVAT9_2{i,1}=AVAT9_2{i,1}   
              else
               AVAT9_2{i,1}=AVAT9_2{i,1}+ ones(1,N)*FV{i,i}*FB{i,j}*FY{j,t} 
               end
          end
              
      end
    end
      
   for i=7:1:14
      AVAT{i,9}=AVAT9_1{i,1}+AVAT9_2{i,1}
   end
  
    csvwrite('AVATX2007.csv',AVAT)   
    
 
    
    
    
    
  
    %%%%%%%%%%%%%计算第12项
    
    AVAT12_1=cell(S,1)
    
    for i=7:1:14
        AVAT12_1{i,1}=0
      for j=1:1:6
             AVAT12_1{i,1}=AVAT12_1{i,1}+ ones(1,N)*FV{i,i}*FB{i,i}*FY{i,j}    
      end
    end
    
     AVAT12_2=cell(S,1)
     for i=7:1:14
       AVAT12_2{i,1}=0
      for j=15:1:S
          AVAT12_2{i,1}= AVAT12_2{i,1}+ ones(1,N)*FV{i,i}*FB{i,i}*FY{i,j} 
       end  
     end
      
   for i=7:1:14
      AVAT{i,12}=AVAT12_1{i,1}+AVAT12_2{i,1}
   end
  
    csvwrite('AVATX2007.csv',AVAT)     
    
    
   %%%%%%%%%%%%%计算第13项
    
    AVAT13_1=cell(S,1)
    
    for i=7:1:14
        AVAT13_1{i,1}=0
        for j=7:1:14
            if j==i
               AVAT13_1{i,1}=AVAT13_1{i,1}
            else
          for t=1:1:6
             AVAT13_1{i,1}=AVAT13_1{i,1}+ ones(1,N)*FV{i,i}*FB{i,j}*FY{j,t} 
          end
            end
       end
    end 
     AVAT13_2=cell(S,1)
     
     for i=7:1:14
       AVAT13_2{i,1}=0
    for j=7:1:14
            if j==i
              AVAT13_2{i,1}=AVAT13_2{i,1}
            else
             for t=15:1:S      
          AVAT13_2{i,1}= AVAT13_2{i,1}+ ones(1,N)*FV{i,i}*FB{i,j}*FY{j,t} 
             end  
            end
    end
     end
       
   for i=7:1:14
      AVAT{i,13}=AVAT13_1{i,1}+AVAT13_2{i,1}
   end
  
    csvwrite('AVATX2007.csv',AVAT)    
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
