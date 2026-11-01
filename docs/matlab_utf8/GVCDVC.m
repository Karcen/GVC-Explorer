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
    
  

    
    
 
          
            

  
  
  
  
    
    
      